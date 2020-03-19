class Target:
    """
    This must be consist of <app_label>.<modal>.<field>
    """
    pass


class StorageProvider:
    S3 = 's3'
    CLOUDINARY = 'cloudinary'


PROVIDERS = (StorageProvider.S3, StorageProvider.CLOUDINARY)
