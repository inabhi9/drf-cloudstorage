import os
from pathlib import Path

import cloudinary.uploader
from cloudinary.exceptions import Error
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields
from django.db import models, transaction
from django.db.models import Manager, Model
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from . import helper
from .constants import StorageProvider
from .errors import UploadError
from .helper import CloudinaryHelper


class StorageProviderManagerMixin:
    @classmethod
    def upload(cls, f, directory, use_filename=True):
        raise NotImplementedError

    def create_and_upload(self, f, **kwargs):
        """
        :param filename f:
        :param kwargs:
            :bool use_filename:
            :content_type:
            :str content_field:
            :str target:
            :int object_id:
        :return:
        """
        content_type = kwargs.get('content_type') or None
        content_field = kwargs.get('content_field') or None
        target = kwargs.pop('target', None)
        link_target = kwargs.pop('link_target', False)
        use_filename = kwargs.pop('use_filename', False)

        assert target or (content_type and content_field)

        # resolve target
        if target:
            content_type, content_field = self._parse_target(target)
            kwargs.update({'content_type': content_type, 'content_field': content_field})

        upload_dir = self._contenttype_upload_dir(content_type, content_field)

        with transaction.atomic():
            kwargs.update({'url': '', 'upload_resp': None})
            cloudfile = self.create(**kwargs)

            url, resp = self.upload(f, upload_dir, use_filename=use_filename)
            cloudfile.url = url
            cloudfile.upload_resp = resp
            cloudfile.save()

            try:
                if link_target is True:
                    cloudfile.link_to_target()
            except AssertionError:
                pass

        return cloudfile

    @classmethod
    def _parse_target(cls, target):
        app_label, model, field = target.lower().split('.')

        content_type = ContentType.objects.get_by_natural_key(app_label, model)

        return content_type, field

    @classmethod
    def _contenttype_upload_dir(cls, contenttype, field=''):
        return '%s__%s__%s'.rstrip('_') % (contenttype.app_label, contenttype.model, field)

    @classmethod
    def _get_file_name(cls, f, use_filename):
        if isinstance(f, str):
            filename = helper.path_leaf(f)
        else:
            filename = f.name

        if use_filename is False:
            filename = '%s_%s' % (get_random_string(5), filename)

        # Slugify only file name without extension
        filename_, ext = os.path.splitext(filename)
        filename_ = slugify(filename_)
        ext = ''.join(Path(filename).suffixes)

        return '%s%s' % (filename_, ext)


class S3FileManager(Manager, StorageProviderManagerMixin):
    @staticmethod
    def boto_s3():
        """
        `django_boto.s3` tries to import AWS settings when initialized. Since we provide multiple
        storage options, we want it to fail when the actual upload() is called

        :return django_boto.s3:
        """
        import django_boto.s3

        return django_boto.s3

    @classmethod
    def upload(cls, f, directory, use_filename=False):
        filename = cls._get_file_name(f, use_filename)

        try:
            url = cls.boto_s3().upload(f, name=filename, prefix=directory)
            resp = {'prefix': directory, 'name': filename, 'storage': StorageProvider.S3}
            return url, resp
        except Exception as e:
            raise UploadError from e


class CloudinaryFileManager(Manager, StorageProviderManagerMixin):
    @classmethod
    def upload(cls, f, directory, use_filename=True):
        assert settings.CLOUDINARY_BASE_PATH is not None, 'Define Cloudinary base path'

        path = '%s/%s' % (settings.CLOUDINARY_BASE_PATH, directory)
        try:
            response = cloudinary.uploader.upload(f, folder=path, use_filename=True,
                                                  invalidate=True, resource_type='auto')
            response['storage'] = StorageProvider.CLOUDINARY
        except Error as e:
            raise UploadError from e

        return response['secure_url'], response


class CloudFileManager(Manager):
    def create_and_upload(self, f, **kwargs):
        storage = kwargs.pop('storage')

        if storage == StorageProvider.CLOUDINARY:
            manager = self.model.cloudinary
        elif storage == StorageProvider.S3:
            manager = self.model.s3
        else:
            raise Exception

        return manager.create_and_upload(f, **kwargs)


class AbstractCloudFile(Model):
    """
    Class to store files metadata
    """
    name = models.CharField(max_length=50, default='', blank=True)
    #: File url
    url = models.URLField()
    #: response received from uploading service
    upload_resp = pg_fields.JSONField(blank=True, editable=False, null=True)
    #: Target model name
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True)
    #: Represents the model field
    content_field = models.CharField(max_length=50, blank=True, null=True)
    #: Target object pk
    object_id = models.CharField(max_length=10, null=True)

    content_object = GenericForeignKey('content_type', 'object_id')

    objects = CloudFileManager()

    s3 = S3FileManager()
    cloudinary = CloudinaryFileManager()

    class Meta:
        abstract = True
        db_table = 'cloudstorage_file'
        default_permissions = ('add', 'change', 'delete', 'view')

    @property
    def storage_provider(self):
        return self.upload_resp['storage']

    @property
    def extra(self):
        if self.storage_provider == StorageProvider.CLOUDINARY:
            return self._cloudinary_extra

        return {}

    def link_to_target(self):
        """
        Sets foreign key or add to the object located by content_type, object_id and content_field

        :return Model: Object that is linked
        """

        assert self.object_id is not None

        model_cls = self.content_type.model_class()
        field = model_cls._meta.get_field(self.content_field)
        has_many_files = issubclass(field.__class__, models.ManyToManyField)
        has_one_file = issubclass(field.__class__, models.ForeignKey)
        obj = model_cls.objects.get(pk=self.object_id)

        if has_many_files:
            getattr(obj, self.content_field).add(self)
        elif has_one_file:
            setattr(obj, self.content_field, self)
            obj.save(update_fields=[self.content_field])
        else:
            raise NotImplementedError

        return obj

    def download(self):
        """
        :return TemporaryFile:
        """
        if self.upload_resp['storage'] == 's3':
            return S3FileManager.boto_s3().download(self.upload_resp['name'],
                                                    self.upload_resp['prefix'])

        raise NotImplementedError

    @property
    def _cloudinary_extra(self):
        cloudinary_cls = CloudinaryHelper(self.upload_resp)

        return {
            'thumbnail': cloudinary_cls.edit('c_scale,h_50'),
            'small': cloudinary_cls.edit('c_scale,h_250'),
            'public_id': self.upload_resp.get('public_id'),
            'resource_type': self.upload_resp.get('resource_type'),
            'file_name': cloudinary_cls.file_name,
            'file_name_short': helper.shorten_str(cloudinary_cls.file_name,
                                                  append='.%s' % cloudinary_cls.format)
        }


class CloudFile(AbstractCloudFile):
    #: User who uploads the file i.e. owner of the object
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, editable=False,
                              null=True, on_delete=models.SET_NULL)
