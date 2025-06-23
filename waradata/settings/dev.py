from .common import *

DEBUG = True

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-default-dev-key')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'waradata_db',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '19051905'
    }
}

