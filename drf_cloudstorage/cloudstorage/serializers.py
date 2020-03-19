import mimetypes

import humanfriendly
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from cloudstorage.constants import PROVIDERS
from cloudstorage.errors import CloudFileError
from cloudstorage.models import CloudFile, StorageProviderManagerMixin


class CloudFileSerializer(ModelSerializer):
    file = serializers.FileField(required=True, write_only=True)
    target = serializers.CharField(required=True, write_only=True, max_length=500)
    extra = serializers.DictField(read_only=True)
    storage = serializers.ChoiceField(choices=PROVIDERS, required=True, write_only=True)
    link_target = serializers.BooleanField(write_only=True, default=True)

    class Meta:
        model = CloudFile
        read_only_fields = ('url', 'owner')
        owner_field = 'owner'
        exclude = ('upload_resp',)

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

    def create(self, validated_data):
        f = validated_data.pop('file', None)
        return CloudFile.objects.create_and_upload(f, **validated_data)


class CloudFileListSerializer(ModelSerializer):
    class Meta:
        model = CloudFile
        fields = ('url', 'id', 'extra', 'name', 'owner', 'created_at')
