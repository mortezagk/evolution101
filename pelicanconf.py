#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'مرتضی قربانی کاری'
SITENAME = 'فرگشت ۱۰۱'
SITEURL = 'evolution101.ir'

PATH = 'content'

STATIC_PATHS = [
    'extra',
]

EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'theme/images/favicon.ico'},
    'extra/cc.heart.black.png': {'path': 'theme/images/cc.heart.black.png'},

}

TIMEZONE = 'Asia/Tehran'

DEFAULT_LANG = 'fa'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

THEME = 'theme/bookstrap'

DISPLAY_CATEGORIES_ON_MENU = True
#TWITTER_USERNAME = "mortezagk"

ARTICLE_ORDER_BY = 'filename'

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
        },
        'markdown.extensions.extra': {},
        # optionally, more extensions,
        # e.g. markdown.extensions.meta
    },
    'output_format': 'html5',
}
