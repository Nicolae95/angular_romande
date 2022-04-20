# flake8: noqa

from __future__ import absolute_import

from os import environ

from .base import *

DEBUG = True
# DEBUG = False
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


ALLOWED_HOSTS = ['172.28.150.23', '172.17.150.51', 'S1EMPPRD.pegase.lan', 's1empprddb.pegase.lan', 
                 '172.17.150.22', 'S1EMPPRDDB', 's2smtprd.pegase.lan', 's1empprd.re-dmz.ch', 's1empprddb.pegase.lan']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = get_env_setting('EMAIL_HOST')
# EMAIL_HOST_PASSWORD = get_env_setting('EMAIL_HOST_PASSWORD')
# EMAIL_HOST_USER = get_env_setting('EMAIL_HOST_USER')
# EMAIL_PORT = get_env_setting('EMAIL_PORT')
# EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME
# EMAIL_USE_TLS = True
# SERVER_EMAIL = EMAIL_HOST_USER

MAIL_SERVER = 'mail.romande-energie.ch'
MAIL_NAME = 'entreprises@romande-energie.ch'
MAIL_PASSWORD = ''


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'romande',
        'USER': 'romande',
        'PASSWORD': 'emp2018',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# CACHES = {}

SECRET_KEY = get_env_setting('SECRET_KEY')

# CORS_ORIGIN_WHITELIST = (')
# CORS_ORIGIN_ALLOW_ALL = True
