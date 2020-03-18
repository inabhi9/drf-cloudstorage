from django.db import models

from cloudstorage.fields import CloudFileField, ManyCloudFileField


class Example(models.Model):
    all_file = CloudFileField('cloudstorage.CloudFile', on_delete=models.SET_NULL, null=True,
                              min_file_size='1KB', max_file_size='2MB', related_name='+',
                              blank=True)
    image_file = CloudFileField('cloudstorage.CloudFile', on_delete=models.SET_NULL, null=True,
                                min_file_size='1KB', max_file_size='2MB', blank=True,
                                allowed_mime_types=('image/jpeg', 'image/png', 'image/jpg'))
    attachments = ManyCloudFileField('cloudstorage.CloudFile', blank=True,
                                     min_file_size='1KB', max_file_size='2MB',
                                     related_name='example_attachments')
