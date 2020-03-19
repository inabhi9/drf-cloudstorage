import logging

import cloudinary
from django.conf import settings

L = logging.getLogger(__name__)

try:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )
except AttributeError:
    L.warning('Cloudinary settings attributes are missing and storage will not be available.')
