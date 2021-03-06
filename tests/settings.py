from yurika.settings import *  # flake8: noqa


INSTALLED_APPS += [
    'tests.integration.mortar.testapp',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'TEST': {'NAME': 'test.sqlite3'},
    }
}


# Weak hashing algorithm for performance improvements
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']


# Store outgoing test emails in django.core.mail.outbox`.
# https://docs.djangoproject.com/en/2.0/topics/testing/tools/#email-services
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Use stub broker in testing
DRAMATIQ_BROKER['BROKER'] = 'dramatiq.brokers.stub.StubBroker'
DRAMATIQ_BROKER['OPTIONS'] = {}


# Disable most logging
LOGGING['loggers']['scrapy']['level'] = 'ERROR'
LOGGING['root']['level'] = 'ERROR'
