"""
Django settings

Generated by 'django-admin startproject' using Django 1.10, and customized a
bit to add a logging config and a few other tweaks.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
# This generates a secret key the first time it's accessed
secret_key_path = os.path.join(BASE_DIR, "secret.txt")
if os.path.exists(secret_key_path):
    SECRET_KEY = open(secret_key_path, "r").read().strip()
else:
    import django.utils.crypto
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    SECRET_KEY = django.utils.crypto.get_random_string(50, chars)
    # Create the file such that only the current user can read it
    fd = os.open(secret_key_path,
                 os.O_WRONLY|os.O_CREAT|os.O_TRUNC,
                 0o600)
    with os.fdopen(fd, "w") as keyout:
        keyout.write(SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'appname',

    # Uncomment for oauth
    #'oauth',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication Backends
# https://docs.djangoproject.com/en/1.10/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',

    # Uncomment for oauth authentication
    #'oauth.authbackend.OAuthBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Our preferred logging configuration.
# Django takes the LOGGING setting and passes it as-is into Python's
# logging dict-config function (logging.config.dictConfig())
# For information about how Python's logging facilities work, see
# https://docs.python.org/3.5/library/logging.html
#
# The brief 3-paragraph summary is:
# Loggers form a tree hierarchy. A log message is emitted to a logger
# somewhere in this tree, and the hierarchy is used to determine what to do
# with the message.
#
# Each logger may have a level. A message also has a level. A message is
# emitted if its level is greater than its logger's level, or in case its
# logger doesn't have a level, the next one down in the hierarchy (repeat all
# the way until it hits the root, which always has a level). Note that the
# first logger with a level is the ONLY logger whose level is used in this
# decision.
#
# Each logger may have zero or more handlers, which determine what to do with
# a message that is to be emitted (e.g. print it, email it, write to a file). A
# message that passes the level test travels down the hierarchy, being sent
# to each handler at each logger, until it reaches the root logger or a
# logger marked with propagate=False. Each handler may do level checks or
# additional filtering of its own.
#
#
# Typically, you will want to log messages within your application under your
# own logger or a sublogger for each component, often named after the modules,
# such as "myapp.views",  "myapp.models", etc. Then you can customize what to
# do with messages from different components of your app.
#
# You don't need to declare a loggers in the config; they are created
# implicitly with no level and no handlers when calling logging.getLogger()
#
#
# Note: if you are getting a lot of DEBUG or INFO level log messages from
# third party libraries, a good change to make is:
# * Set the root logger level to "WARNING"
# * Add a logger for your project and set its level to DEBUG or INFO
# * Use your logger or a sub-logger of it throughout your project
import sys
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    "formatters": {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s%(reset)s [%(name)s] "
                      "%(message)s",
            "log_colors": {"DEBUG": "cyan",
                           "INFO": "white",
                           "WARNING": "yellow",
                           "ERROR": "red",
                           "CRITICAL": "white,bg_red",
                           }
        },
        "nocolor": {
            "format": "%(asctime)s %(levelname)-8s [%(name)s] "
                      "%(message)s",
            "datefmt": '%Y-%m-%d %H:%M:%S',
        },
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "formatter": "color" if sys.stderr.isatty() else "nocolor",
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    "loggers": {
        "django": {
            # Django logs everything it does under this handler. We want
            # the level to inherit our root logger level and handlers,
            # but also add a mail-the-admins handler if an error comes to this
            # point (Django sends an ERROR log for unhandled exceptions in
            # views)
            "handlers": ["mail_admins"],
            "level": "NOTSET",
        },
        "django.db": {
            # Set to DEBUG to see all database queries as they happen.
            # Django only sends these messages if settings.DEBUG is True
            "level": "INFO",
        },
        "py.warnings": {
            # This is a built-in Python logger that receives warnings from
            # the warnings module and emits them as WARNING log messages*. By
            # default, this logger prints to stderr. We override that here so
            # that it simply inherits the root logger's handlers
            #
            # * Django enables this behavior by calling
            #   https://docs.python.org/3.5/library/logging.html#logging.captureWarnings
        }
    },
    "root": {
        "handlers": ["stderr"],
        "level": "DEBUG" if DEBUG else "INFO",
    }
}

from django.core.urlresolvers import reverse_lazy
LOGIN_URL = reverse_lazy("login")
LOGOUT_URL = reverse_lazy("logout")
LOGIN_REDIRECT_URL = reverse_lazy("home")
