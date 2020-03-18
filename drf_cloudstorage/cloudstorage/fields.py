import humanfriendly
from django.core import checks
from django.db.models import ForeignKey, ManyToManyField

from cloudstorage.models import AbstractCloudFile


class CustomAttributeFieldMixin:
    def __init__(self, *args, **kwargs):
        """
        :param kwargs:
        """

        self.allowed_mime_types = kwargs.pop('allowed_mime_types', None)
        self.min_file_size = kwargs.pop('min_file_size', None)
        self.max_file_size = kwargs.pop('max_file_size', None)

        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_cloudfile_subclass(),
            *self._check_validation_attribute(),
        ]

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
            self.min_file_size = humanfriendly.parse_size(self.min_file_size, binary=True)
        except TypeError:
            return [
                checks.Error(
                    "CloudFileFields must define a 'min_file_size' attribute.",
                    obj=self,
                    id='fields.E120',
                )
            ]

        try:
            self.max_file_size = humanfriendly.parse_size(self.max_file_size, binary=True)
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
