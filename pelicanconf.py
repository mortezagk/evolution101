#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'مرتضی قربانی کاری'
SITENAME = 'فرگشت ۱۰۱'
SITEURL = 'www.evolution101.ir'

PATH = 'content'
STATIC_PATHS = ['extra']
OUTPUT_PATH = '../evo-out/'

EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'theme/images/favicon.ico'},
    'extra/cc.heart.black.png': {'path': 'theme/images/cc.heart.black.png'},
    'extra/CNAME': {'path': ''},
    'extra/robots.txt': {'path': ''},
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

DISPLAY_CATEGORIES_ON_MENU = False

GOOGLE_CUSTOM_SEARCH_SIDEBAR = False

CATEGORY_REGEX_SUBSTITUTIONS = [(r'(mqdmh)', 'ch0'),
			                	(r'(fsl wl: lgwh)', 'ch1'),
		                		(r'(fsl dwm: szwkhrh)','ch2'),
                                (r'(fsl swm: frgsht khrd)','ch3'),
                                (r'(fsl chhrm: gwnhzyy)','ch4'),
                                (r'(fsl pnjm: frgsht khln)','ch5'),
                                (r"(fsl shshm: msy'l mhm)",'ch6'),
                                ]

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


#SITEMAP GENERATOR
PLUGIN_PATHS = ['../pelican-plugins/']
PLUGINS = ['sitemap']

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
                   },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
                    }
           }