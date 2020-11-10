drf-cloudstorage
================
Aim of this app to simplify the static file upload to a cloud needed to integrate with 
django rest framework app.

**Motivation:**  
Static file upload is needed in many part of an app. 
Creating different routes for each module that supports multipart data and validation is quite
tedious and cumbersome; and also difficult for frontend development.

## Features

* Upload to S3 and Cloudinary.
* Single endpoint to manage files.
* File mime type and size validation.
* Automatic ForeignKey / ManyToManyField link. 

## Installation

    python setup.py install
    
the pip way

    pip install drf-cloudstorage
    
    
## Dependency

- Python 3.6.x or later
- Django >= 2.2.x <= 3.0.x
- Postgres 9.x or later
- Django-rest-framework 3.8.x

## To Do:

* Implement GC
* Docs
* Test S3
* CI integration
* PyPI upload
