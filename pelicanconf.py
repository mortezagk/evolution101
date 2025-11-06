#!/usr/bin/env python
# -*- coding: utf-8 -*- #
"""Pelican configuration for the فرگشت ۱۰۱ project."""

from __future__ import unicode_literals

import os
from pathlib import Path

PERSIAN_DIGIT_MAP = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def persian_digits(value):
    """Convert ASCII digits in *value* to their Persian equivalents."""

    if value is None:
        return ''

    text = str(value)
    return text.translate(PERSIAN_DIGIT_MAP)

AUTHOR = 'mortezagk'
SITENAME = 'فرگشت ۱۰۱'
SITEURL = os.getenv('SITEURL', 'https://www.evolution101.ir')

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_PATH = str((BASE_DIR / '_build').resolve())
DELETE_OUTPUT_DIRECTORY = os.getenv('PELICAN_CLEAN_OUTPUT', '1') == '1'

PATH = 'content'
STATIC_PATHS = ['extra', 'images']
FILENAME_METADATA = r'(?P<section>\d)(?P<section_index>\d{2})-.*'

EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'theme/images/favicon.ico'},
    'extra/cc.heart.black.png': {'path': 'theme/images/cc.heart.black.png'},
    'extra/CNAME': {'path': 'CNAME'},
    'extra/robots.txt': {'path': 'robots.txt'},
}

TIMEZONE = 'Asia/Tehran'
DEFAULT_LANG = 'fa'
LOCALE = ('fa_IR.UTF-8', 'fa_IR', 'fa', 'en_US.UTF-8', 'en_US')
DEFAULT_DATE_FORMAT = '%Y/%m/%d'

RELATIVE_URLS = os.getenv('PELICAN_RELATIVE_URLS', '1') == '1'

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

THEME = 'theme/bookstrap'

THEME_STATIC_PATHS = ['static']
THEME_TEMPLATES_OVERRIDES = ['theme_overrides/templates']

ARTICLE_ORDER_BY = 'source_path'
DEFAULT_PAGINATION = False
DISPLAY_CATEGORIES_ON_MENU = False
GOOGLE_CUSTOM_SEARCH_SIDEBAR = False

ARTICLE_URL = 'chapter-{section}/{section_index}-{slug}.html'
ARTICLE_SAVE_AS = 'chapter-{section}/{section_index}-{slug}.html'
ARTICLE_TRANSLATION_URL = 'chapter-{section}/{section_index}-{slug}-{lang}.html'
ARTICLE_TRANSLATION_SAVE_AS = 'chapter-{section}/{section_index}-{slug}-{lang}.html'

CATEGORY_REGEX_SUBSTITUTIONS = [(r'(mqdmh)', 'ch0'),
                                (r'(fsl wl: lgwh)', 'ch1'),
                                (r'(fsl dwm: szwkhrh)', 'ch2'),
                                (r'(fsl swm: frgsht khurd)', 'ch3'),
                                (r'(fsl chhrm: gwnhzyy)', 'ch4'),
                                (r'(fsl pnjm: frgsht khln)', 'ch5'),
                                (r"(fsl shshm: msy'l mhm)", 'ch6')]


MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',},
        'markdown.extensions.extra': {},
        'markdown.extensions.md_in_html': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {
            'permalink': '',
            'title': 'فهرست'},},
        # optionally, more extensions,
        # e.g. markdown.extensions.meta
    'output_format': 'html5',}

JINJA_ENVIRONMENT = {
    'trim_blocks': True,
    'lstrip_blocks': True,
}

JINJA_FILTERS = {
    'persian_digits': persian_digits,
}

PLUGINS = []

DIRECT_TEMPLATES = ('index', 'categories', 'authors', 'archives', 'search_index')

SEARCH_INDEX_SAVE_AS = 'search-index.json'
SEARCH_INDEX_URL = 'search-index.json'
