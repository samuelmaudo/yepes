# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from hashlib import sha1

from django.conf import settings
from django.utils.encoding import force_bytes


# Built-in search engine #######################################################

SEARCH_MAX_QUERY_LEN = 100
SEARCH_MIN_QUERY_LEN = 3
SEARCH_MIN_WORD_LEN = 3
SEARCH_PREPARE_WORD = 'yepes.managers.searchable.prepare_word'
SEARCH_RESULT_LIMIT = 1000
SEARCH_VOWELS_REPLACE = 'yepes.managers.searchable.vowels_replace'


# Mint cache ###################################################################

MINT_CACHE_DELAY_SECONDS = 60
MINT_CACHE_SECONDS = 600


# Multilingual #################################################################

MULTILINGUAL_DEFAULT = 'en'
MULTILINGUAL_FAIL_SILENTLY = True
MULTILINGUAL_FALL_BACK_TO_DEFAULT = False


# Phased #######################################################################

PHASED_KEEP_CONTEXT = False
PHASED_SECRET_DELIMITER = sha1(force_bytes(settings.SECRET_KEY)).hexdigest()


# SSL ##########################################################################

# Enable SSL
SSL_ENABLED = False

# Secure paths
SSL_PATHS = ('/admin', '/cache', '/settings')

# SSL port
SSL_PORT = 443


# Thumbnails ###################################################################

THUMBNAIL_QUALITY = 90
THUMBNAIL_SUBDIR = 'thumbs'


# View cache ###################################################################

VIEW_CACHE_ALIAS = 'default'
VIEW_CACHE_AVAILABLE = True
VIEW_CACHE_DELAY_SECONDS = 60
VIEW_CACHE_SECONDS = 600

