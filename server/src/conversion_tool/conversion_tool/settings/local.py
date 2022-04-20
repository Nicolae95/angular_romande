# flake8: noqa

from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

MAIL_SERVER = 'smtp.gmail.com:587'
MAIL_NAME = 'non.commodity.data@gmail.com'
MAIL_PASSWORD = 'energymarketprice'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'HOST': 'db',
#         'PORT': 5432,
#     }
# }
#

# Viorel
#DATABASES = {
#    'default': {
#		'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'demo1',
#        'USER': 'postgres',
#        'PASSWORD': 'postgres',
#        'HOST': 'localhost',
#        'PORT': '5432',
#    }
#}


DATABASES = {
    'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zeno',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}



# DATABASES = {
#     'default': {
# 		'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'n_demo',
#         'NAME': 'demo',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


#  Vadim
# DATABASES = {
#     'default': {
# 		'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'romande2',
#         'USER': 'postgres',
#         'PASSWORD': 'Moldova82',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'conversion_tool.db',
#     }
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

INSTALLED_APPS += (
    'django_extensions',
    'debug_toolbar',
)

INTERNAL_IPS = ('127.0.0.1',)


MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': True,
}

CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = []
