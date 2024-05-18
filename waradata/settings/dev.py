from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-$%br2!j=q9+)ghjl(m6ko%lje1-fxj37bh5d+fyh-94lj+6olc'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'waradata_db',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '19051905'
    }
}

