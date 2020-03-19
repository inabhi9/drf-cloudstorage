'''
pytz setup script
'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

me = 'Abhinav Kotak'
memail = 'in.abhi9@gmail.com'

packages = ['drf_cloudstorage', 'drf_cloudstorage.migrations']
package_dir = {'drf_cloudstorage': 'src/drf_cloudstorage'}
install_requires = open('requirements.txt', 'r').readlines()

setup(
    name='drf_cloudstorage',
    version='1.0.0',
    zip_safe=True,
    description='Cloudstorage API app for DRF. Supports S3 and Cloudinary',
    author=me,
    author_email=memail,
    maintainer=me,
    maintainer_email=memail,
    install_requires=install_requires,
    url='https://github.com/inabhi9/drf-cloudstorage',
    license=open('LICENSE', 'r').read(),
    keywords=['djangorestframework', 'drf', 'cloudstorage'],
    packages=packages,
    package_dir=package_dir,
    platforms=['Independant'],
    classifiers=[
        'Development Status :: 1 - beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
