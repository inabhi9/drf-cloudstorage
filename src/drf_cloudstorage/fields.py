import humanfriendly
from django.core import checks
from django.db.models import ForeignKey, ManyToManyField

from drf_cloudstorage.models import AbstractCloudFile


class CustomAttributeFieldMixin:
    def __init__(self, *args, **kwargs):
        """
        :param kwargs:
        """

        self.allowed_mime_types = kwargs.pop('allowed_mime_types', None)
        self._min_file_size = kwargs.pop('min_file_size', None)
        self._max_file_size = kwargs.pop('max_file_size', None)

        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_cloudfile_subclass(),
            *self._check_validation_attribute(),
        ]

    @property
    def min_file_size(self):
        """
        For some reason, when app is used with uwsgi, self.min_file_size assigned in .check()
        does not preserved.

        :return int: min_file_size in bytes
        """
        return humanfriendly.parse_size(self._min_file_size, binary=True)

    @property
    def max_file_size(self):
        """
        For some reason, when app is used with uwsgi, self.max_file_size assigned in .check()
        does not preserved.

        :return int: max_file_size in bytes
        """
        return humanfriendly.parse_size(self._max_file_size, binary=True)

    def _check_cloudfile_subclass(self):
        if issubclass(self.related_model, AbstractCloudFile) is False:
            return [
                checks.Error(
                    'This field is not related to a subclass of %s' % (
                        'drf_cloudstorage.AbstractCloudFile'
                    ),
                    hint="Use foreign key to subclass of drf_cloudstorage.AbstractCloudFile",
                    obj=self,
                    id='fields.E306',
                )
            ]

        return []

    def _check_validation_attribute(self):
        try:
            humanfriendly.parse_size(self._min_file_size, binary=True)
        except TypeError:
            return [
                checks.Error(
                    "CloudFileFields must define a 'min_file_size' attribute.",
                    obj=self,
                    id='fields.E120',
                )
            ]

        try:
            humanfriendly.parse_size(self._max_file_size, binary=True)
        except TypeError:
            return [
                checks.Error(
                    "CloudFileFields must define a 'max_file_size' attribute.",
                    obj=self,
                    id='fields.E120',
                )
            ]

        return []


class CloudFileField(CustomAttributeFieldMixin, ForeignKey):
    pass


class ManyCloudFileField(CustomAttributeFieldMixin, ManyToManyField):
    pass
