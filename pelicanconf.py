"""Pelican configuration for the فرگشت ۱۰۱ project."""

import json
import os
import re
import sys
from html import unescape
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
SITEURL = os.getenv('SITEURL', 'https://evolution101.ir')
# Absolute site address for canonical links; SITEURL itself becomes relative
# in templates when RELATIVE_URLS is on.
CANONICAL_SITEURL = SITEURL.rstrip('/')

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_PATH = str((BASE_DIR / '_build').resolve())
DELETE_OUTPUT_DIRECTORY = os.getenv('PELICAN_CLEAN_OUTPUT', '1') == '1'

PATH = 'content'
STATIC_PATHS = ['extra']
FILENAME_METADATA = r'(?P<section>\d)(?P<section_index>\d{2})-.*'

EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'theme/images/favicon.ico'},
    'extra/logo-light.png': {'path': 'theme/images/logo-light.png'},
    'extra/CNAME': {'path': 'CNAME'},
    'extra/robots.txt': {'path': 'robots.txt'},
}

TIMEZONE = 'Asia/Tehran'
DEFAULT_LANG = 'fa'
# C.UTF-8 exists on every modern Linux, so the build never warns (and never
# fails under --fatal warnings) on machines without fa/en locales.
LOCALE = ('fa_IR.UTF-8', 'en_US.UTF-8', 'C.UTF-8')
DEFAULT_DATE_FORMAT = '%Y/%m/%d'

RELATIVE_URLS = os.getenv('PELICAN_RELATIVE_URLS', '1') == '1'

# No feeds: the book is not a blog.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

THEME = 'theme/bookstrap'

THEME_TEMPLATES_OVERRIDES = ['theme_overrides/templates']

ARTICLE_ORDER_BY = 'source_path'

# Addresses are <chapter>-<chapter slug>/<page order>-<page slug>/, e.g.
# 4-speciation/06-cospeciation/. Each chapter file's Slug holds that path
# (a chapter cover is just the chapter folder). Links point at index.html
# explicitly so the built site also works when opened straight from disk.
ARTICLE_URL = '{slug}/index.html'
ARTICLE_SAVE_AS = '{slug}/index.html'

# Category slugs (ch0-ch6) only feed the sidebar's open/closed state; the
# category, tag, author and archive listing pages themselves are not built.
CATEGORY_REGEX_SUBSTITUTIONS = [(r'(mqdmh)', 'ch0'),
                                (r'(fsl wl: lgwh)', 'ch1'),
                                (r'(fsl dwm: szwkhrh)', 'ch2'),
                                (r'(fsl swm: frgsht khurd)', 'ch3'),
                                (r'(fsl chhrm: gwnhzyy)', 'ch4'),
                                (r'(fsl pnjm: frgsht khln)', 'ch5'),
                                (r"(fsl shshm: msy'l mhm)", 'ch6')]


MARKDOWN = {
    'extension_configs': {
        # extra brings footnotes, attr_list, tables and md_in_html with it.
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        # toc gives the headings their ids, which the footnote and heading
        # links point at. No page uses a [TOC] marker, so the table itself is
        # never generated.
        'markdown.extensions.toc': {'permalink': ''},
    },
    'output_format': 'html5',
}

JINJA_ENVIRONMENT = {
    'trim_blocks': True,
    'lstrip_blocks': True,
}

def plain_text(html, length=None):
    """Visible text of *html* without footnote markers or images, optionally
    shortened to about *length* characters at a word boundary."""

    html = re.sub(r'<sup[^>]*>.*?</sup>', '', html or '', flags=re.S)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = unescape(re.sub(r'\s+', ' ', text)).strip()
    if length and len(text) > length:
        text = text[:length].rsplit(' ', 1)[0].rstrip('،,.:؛') + '…'
    return text


def to_json(value):
    """JSON for the search index, keeping Persian text as UTF-8 rather than
    \\uXXXX escapes (a third of the size)."""

    return json.dumps(value, ensure_ascii=False)


JINJA_FILTERS = {
    'persian_digits': persian_digits,
    'plain_text': plain_text,
    'to_json': to_json,
}

# Footnote entries come in two kinds: an English term on its own ("Lineage")
# and an English term with a Persian gloss ("Phylogeny: روابط فرگشتی…"). Both
# sit in a right-to-left list, which is what the glossed ones want. The
# all-English ones do not: their last run ends at the left margin, so the "↩"
# backref lands to the left of the term instead of after it. CSS cannot ask
# whether an entry has Persian in it, so the ones that have none are marked
# here and style.css turns just those left-to-right.

PERSIAN_RANGE = re.compile(r'[؀-ۿ]')
# The class goes on the <li>, not the paragraph inside it: the list marker is
# drawn by the item, so the number only moves with the text when the item
# itself is left-to-right.
FOOTNOTE_ENTRY = re.compile(r'(<li id="fn:[^"]*")(>)(.*?)(</li>)', re.S)


def latin_footnotes(content):
    """Add class="footnote-latin" to footnote entries with no Persian text."""

    def mark(match):
        open_tag, close_bracket, body, end = match.groups()
        # The backref's title ("Jump back to footnote 1 in the text") is
        # English but never displayed, so it must not count as content.
        visible = re.sub(r'<a class="footnote-backref".*?</a>', '', body, flags=re.S)
        if PERSIAN_RANGE.search(visible):
            return match.group(0)
        return f'{open_tag} class="footnote-latin"{close_bracket}{body}{end}'

    return FOOTNOTE_ENTRY.sub(mark, content)


def mark_latin_footnotes(instance):
    if instance._content and 'footnote-backref' in instance._content:
        instance._content = latin_footnotes(instance._content)


def register():
    from pelican import signals
    signals.content_object_init.connect(mark_latin_footnotes)


PLUGINS = [sys.modules[__name__]]

DIRECT_TEMPLATES = ('sitemap', 'search_index')
SITEMAP_SAVE_AS = 'sitemap.xml'
# Full text of every page for the on-site search (pages/search.html). A .js
# file rather than JSON so it also loads when the site is opened from disk.
SEARCH_INDEX_SAVE_AS = 'search-index.js'
CATEGORY_SAVE_AS = ''
TAG_SAVE_AS = ''
AUTHOR_SAVE_AS = ''
