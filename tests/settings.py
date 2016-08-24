# -*- coding:utf-8 -*-

# This is an example test settings file for use with the Django test suite.
#
# The 'sqlite3' backend requires only the ENGINE setting (an in-memory
# database will be used). All other backends will require a NAME and
# potentially authentication information. See the following section in the
# docs for more information:
#
# https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/
#
# The different databases that Django supports behave differently in certain
# situations, so it is recommended to run the test suite against as many
# database backends as possible. You may want to create a separate settings
# file for each of the backends you test against.

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    },
}

DEBUG = True

# These 'tests.migrations' modules don't actually exist, but this lets us
# skip creating migrations for the test models.
MIGRATION_MODULES = {
    'auth': 'django.contrib.auth.migrations_',
    'contenttypes': 'django.contrib.contenttypes.migrations_',
    'sessions': 'django.contrib.sessions.migrations_',
}

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

SECRET_KEY = 'yepes_secret_key_for_running_tests'

USE_TZ = True
