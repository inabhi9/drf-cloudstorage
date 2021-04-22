import mimetypes

import humanfriendly
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from drf_cloudstorage.constants import PROVIDERS
from drf_cloudstorage.errors import CloudFileError
from drf_cloudstorage.models import CloudFile, StorageProviderManagerMixin


class CloudFileSerializer(ModelSerializer):
    file = serializers.FileField(required=True, write_only=True)
    target = serializers.CharField(required=True, write_only=True, max_length=500)
    extra = serializers.DictField(read_only=True)
    storage = serializers.ChoiceField(choices=PROVIDERS, write_only=True,
                                      default=getattr(settings, 'CLOUDSTORAGE_DEFAULT_PROVIDER',
                                                      None))
    link_target = serializers.BooleanField(write_only=True, default=True)
    signed_url = serializers.ReadOnlyField()

    class Meta:
        model = CloudFile
        read_only_fields = ('url', 'owner')
        owner_field = 'owner'
        exclude = ('upload_resp',)

    def validate_storage(self, value):
        if not value:
            raise ValidationError(_('This field is required.'))
        return value

    def validate_target(self, value):
        content_type, field = StorageProviderManagerMixin._parse_target(value)
        model_cls = content_type.model_class()
        try:
            field_cls = model_cls._meta.get_field(field)
        except FieldDoesNotExist as e:
            raise ValidationError(e.args[0])

        return value, field_cls, model_cls

    def validate(self, attrs):
        attrs = super().validate(attrs)
        file = attrs.get('file')
        target_str, field_cls, model_cls = attrs.pop('target')
        attrs['target'] = target_str

        self._validate_mime_type(field_cls, file)
        self._validate_file_size(field_cls, file)
        try:
            self._validate_target_object(model_cls, attrs['object_id'])
        except KeyError:
            pass

        return attrs

    def _validate_mime_type(self, remote_field_model_cls, file):
        mt, encoding = mimetypes.guess_type(file.name)
        allowed_mt = getattr(remote_field_model_cls, 'allowed_mime_types', None)

        if allowed_mt is not None and mt not in allowed_mt:
            raise CloudFileError(_('Only %s file types are allowed' % ', '.join(allowed_mt)))

    def _validate_file_size(self, remote_field_model_cls, file):
        min_size = remote_field_model_cls.min_file_size
        max_size = remote_field_model_cls.max_file_size

        if file.size > max_size or file.size < min_size:
            raise CloudFileError(_(
                'File size must be between %s and %s' %
                (humanfriendly.format_size(min_size), humanfriendly.format_size(max_size))
            ))

    def _validate_target_object(self, model_cls, object_id):
        if model_cls.objects.filter(id=object_id).exists() is False:
            raise ValidationError(_(
                "Object id '%s' with provided target does not exist." % object_id
            ))

    def create(self, validated_data):
        f = validated_data.pop('file', None)
        return CloudFile.objects.create_and_upload(f, **validated_data)


class CloudFileListSerializer(ModelSerializer):
    class Meta:
        model = CloudFile
        fields = ('url', 'id', 'extra', 'name', 'owner', 'created_at')


class CloudFileURLSignedListSerializer(ModelSerializer):
    signed_url = serializers.ReadOnlyField()

    class Meta:
        model = CloudFile
        fields = ('url', 'id', 'extra', 'name', 'owner', 'created_at', 'signed_url')
