from rest_framework.exceptions import APIException


class CloudStorageError(APIException):
    pass


class CloudFileError(CloudStorageError):
    status_code = 400


class UploadError(CloudStorageError):
    status_code = 503
