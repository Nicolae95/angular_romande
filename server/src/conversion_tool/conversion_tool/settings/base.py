# flake8: noqa

from os.path import basename, dirname, join, normpath
from sys import path
import os

BASE_DIR = dirname(dirname(__file__))
SITE_ROOT = dirname(BASE_DIR)
SITE_NAME = basename(BASE_DIR)

GEOIP_PATH = os.path.join(BASE_DIR, 'geoip')

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(BASE_DIR)

# LOGIN_REDIRECT_URL = '/index/'

TEMPLATE_DEBUG = False

ADMINS = (
    ('Ann Onymous', 'change.me@gmail.com'),
)

TIME_ZONE = 'CET'
LANGUAGE_CODE = 'en-gb'


# CSRF_COOKIE_AGE = 259200
# CSRF_COOKIE_HTTPONLY = True
# SESSION_COOKIE_PATH = '/;HttpOnly'
# CSRF_COOKIE_SECURE = True
SITE_ID = 1

DATA_UPLOAD_MAX_NUMBER_FIELDS = 50240
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))
MEDIA_URL = '/media/'

STATIC_ROOT = normpath(join(SITE_ROOT, 'static'))
STATIC_URL = '/static/'
# STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (join(BASE_DIR, 'static'),)


# Note: This key should only be used for development and testing.
SECRET_KEY = r"3#b^34xo3le)8*7h4(jjup2f^bn02@u6y)+ul_@8j%gj1&#%wt"


TEMPLATE_DIRS = (
    normpath(join(SITE_ROOT, 'templates')),
)
import os

TEMPLATES = [
{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR,'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',

        ],
    },
},]


MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'client.utils.middleware.MobileDetectionMiddleware',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

ROOT_URLCONF = 'conversion_tool.urls'


DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    # 'django.contrib.admindocs',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    'django_countries',
    'corsheaders',
    # 'channels',
    # 'channels_api'
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'core',
    'geo',
    'companies',
    'client',
    'cockpit',
    'pfc',
    'offers',
    'budget',
    'type',
    'translations',
    'typepondere',
    'datahub'
)

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS


import datetime


# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'asgiref.inmemory.ChannelLayer',
#         'ROUTING': "cockpit.routing.channel_routing",
#     },
# }


# Configure the JWTs to expire after 1 hour, and allow users to refresh near-expiration tokens
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=3),
    'JWT_ALLOW_REFRESH': True,
    'JWT_PAYLOAD_HANDLER': 'client.utils.jwt_payload.jwt_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'client.utils.jwt_payload.jwt_response_payload_handler',

}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'client.serializers.UserSerializer',
}

# Make JWT Auth the default authentication mechanism for Django
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

AUTHENTICATION_BACKENDS = (
    ('django.contrib.auth.backends.ModelBackend'),
)

# Enables django-rest-auth to use JWT tokens instead of regular tokens.
REST_USE_JWT = True
SITE_ID = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

WSGI_APPLICATION = 'conversion_tool.wsgi.application'
