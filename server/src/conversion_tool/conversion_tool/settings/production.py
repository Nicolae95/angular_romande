# flake8: noqa

from __future__ import absolute_import

from os import environ

from .base import *

DEBUG = True
# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

ALLOWED_HOSTS = ['149.56.102.173', '79.137.34.74', '10.4.4.72', 's1empdevdb.pegase.lan', 'energysalesengine.com']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = get_env_setting('EMAIL_HOST')
# EMAIL_HOST_PASSWORD = get_env_setting('EMAIL_HOST_PASSWORD')
# EMAIL_HOST_USER = get_env_setting('EMAIL_HOST_USER')
# EMAIL_PORT = get_env_setting('EMAIL_PORT')
# EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME
# EMAIL_USE_TLS = True
# SERVER_EMAIL = EMAIL_HOST_USER

MAIL_SERVER = 'smtp.gmail.com:587'
MAIL_NAME = 'non.commodity.data@gmail.com'
MAIL_PASSWORD = 'energymarketprice'


# MAIL_SERVER = 'mail.romande-energie.ch'
# MAIL_NAME = 'entreprises@romande-energie.ch'
# MAIL_PASSWORD = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'demo',
        'USER': 'demo',
        'PASSWORD': 'demo2018',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# CACHES = {}

SECRET_KEY = get_env_setting('SECRET_KEY')

# CORS_ORIGIN_WHITELIST = ()
CORS_ORIGIN_ALLOW_ALL = True
