from django.db import models

from drf_cloudstorage.fields import CloudFileField, ManyCloudFileField


class Example(models.Model):
    all_file = CloudFileField('drf_cloudstorage.CloudFile', on_delete=models.SET_NULL, null=True,
                              min_file_size='1KB', max_file_size='2MB', related_name='+',
                              blank=True)
    image_file = CloudFileField('drf_cloudstorage.CloudFile', on_delete=models.SET_NULL, null=True,
                                min_file_size='1KB', max_file_size='2MB', blank=True,
                                allowed_mime_types=('image/jpeg', 'image/png', 'image/jpg'))
    attachments = ManyCloudFileField('drf_cloudstorage.CloudFile', blank=True,
                                     min_file_size='1KB', max_file_size='2MB',
                                     related_name='example_attachments')
