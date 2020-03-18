import os
import tempfile

from django.test import TestCase
from rest_framework import status

from cloudstorage.constants import StorageProvider


class CloudinaryTestCase(TestCase):
    ENDPOINT = '/cloudfiles'

    def test_create(self):
        f = open(os.path.dirname(__file__) + '/fixtures/sample.jpg', 'rb')
        data = {
            'file': f,
            'target': 'example.Example.image_file',
            'provider': StorageProvider.CLOUDINARY
        }

        resp = self.client.post(self.ENDPOINT, data=data, format='multipart')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

    def test_create_invalid_mime(self):
        f = open(os.path.dirname(__file__) + '/fixtures/sample.txt', 'rb')
        data = {
            'file': f,
            'target': 'example.Example.image_file',
            'provider': StorageProvider.CLOUDINARY
        }

        resp = self.client.post(self.ENDPOINT, data=data, format='multipart')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, resp.data)

    def test_create_when_not_mime_defined(self):
        f = self._get_file_with_size(1 * 1024 * 1024, suffix='.random')
        data = {
            'file': f,
            'target': 'example.Example.all_file',
            'provider': StorageProvider.CLOUDINARY
        }

        resp = self.client.post(self.ENDPOINT, data=data, format='multipart')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

    def test_create_invalid_filesize(self):
        f = self._get_file_with_size(3 * 1024 * 1024)

        data = {
            'file': f,
            'target': 'example.Example.image_file',
            'provider': StorageProvider.CLOUDINARY
        }

        resp = self.client.post(self.ENDPOINT, data=data, format='multipart')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, resp.data)

    def test_link_file(self):
        f = open(os.path.dirname(__file__) + '/fixtures/sample.jpg', 'rb')
        data = {
            'file': f,
            'target': 'example.Example.image_file',
            'provider': StorageProvider.CLOUDINARY
        }

        resp = self.client.post(self.ENDPOINT, data=data, format='multipart')
        _id = resp.data['id']

        resp = self.client.post('/examples', data={'image_file': _id})
        print(resp.data)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_many_to_many_files(self):
        f = open(os.path.dirname(__file__) + '/fixtures/sample.jpg', 'rb')
        data = {
            'file': f,
            'target': 'example.Example.attachments',
            'provider': StorageProvider.CLOUDINARY
        }

        resp = self.client.post(self.ENDPOINT, data=data, format='multipart')
        _id = resp.data['id']

        resp = self.client.post('/examples', data={'attachments': [_id]}, format='json')
        print(resp.data)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_many_to_many_files_invalid_file_size(self):
        f = self._get_file_with_size(3 * 1024 * 1024)
        data = {
            'file': f,
            'target': 'example.Example.attachments',
            'provider': StorageProvider.CLOUDINARY
        }

        resp = self.client.post(self.ENDPOINT, data=data, format='multipart')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, resp.data)

    def _get_file_with_size(self, filesize, suffix='.jpg'):
        t = tempfile.NamedTemporaryFile(suffix=suffix)
        t.seek(filesize - 1)
        t.write(b"\0")
        t.seek(0)
        return t
