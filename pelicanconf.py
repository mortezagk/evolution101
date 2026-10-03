"""Pelican configuration for the فرگشت ۱۰۱ project."""

import json
import os
import re
import subprocess
import sys
from datetime import date
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
# Absolute address for canonical links; SITEURL goes relative in templates.
CANONICAL_SITEURL = SITEURL.rstrip('/')

BASE_DIR = Path(__file__).resolve().parent


def last_updated():
    """Latest commit date for the footer (today outside git). Not the build
    date: the monthly scheduled rebuild changes nothing."""

    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs'], cwd=BASE_DIR,
                             capture_output=True, text=True, check=True).stdout.strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    return date.today().isoformat()


LAST_UPDATED = last_updated()

OUTPUT_PATH = str((BASE_DIR / '_build').resolve())
DELETE_OUTPUT_DIRECTORY = os.getenv('PELICAN_CLEAN_OUTPUT', '1') == '1'

PATH = 'content'
STATIC_PATHS = ['extra', 'images']
# Chapters are articles; glossary terms are pages, so they stay out of the chapter nav.
ARTICLE_PATHS = ['chapters']
PAGE_PATHS = ['pages', 'glossary']
FILENAME_METADATA = r'(?P<section>\d)(?P<section_index>\d{2})-.*'

EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'theme/images/favicon.ico'},
    'extra/CNAME': {'path': 'CNAME'},
    'extra/robots.txt': {'path': 'robots.txt'},
}

TIMEZONE = 'Asia/Tehran'
DEFAULT_LANG = 'fa'
# C.UTF-8 always exists, so a missing fa/en locale never fails the build.
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

# evo101/chapter-<N>/<page>/, from each file's Slug; a cover is the chapter
# folder itself. Links name index.html so the site also works from disk.
ARTICLE_URL = '{slug}/index.html'
ARTICLE_SAVE_AS = '{slug}/index.html'

# Same shape for pages, e.g. glossary/amino-acid/.
PAGE_URL = '{slug}/index.html'
PAGE_SAVE_AS = '{slug}/index.html'

# Category slugs (ch0–ch6) only mark the sidebar's open chapter; listing pages aren't built.
CATEGORY_REGEX_SUBSTITUTIONS = [(r'(mqdmh)', 'ch0'),
                                (r'(fsl wl: lgwh)', 'ch1'),
                                (r'(fsl dwm: szwkhrh)', 'ch2'),
                                (r'(fsl swm: frgsht khurd)', 'ch3'),
                                (r'(fsl chhrm: gwnhzyy)', 'ch4'),
                                (r'(fsl pnjm: frgsht khln)', 'ch5'),
                                (r"(fsl shshm: msy'l mhm)", 'ch6')]


MARKDOWN = {
    'extension_configs': {
        # extra: footnotes, attr_list, tables, md_in_html.
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        # toc: heading ids for links (no page uses [TOC]).
        'markdown.extensions.toc': {'permalink': ''},
    },
    'output_format': 'html5',
}

JINJA_ENVIRONMENT = {
    'trim_blocks': True,
    'lstrip_blocks': True,
}

def plain_text(html, length=None):
    """Visible text of *html*, without footnote markers; cut at a word near *length*."""

    html = re.sub(r'<sup[^>]*>.*?</sup>', '', html or '', flags=re.S)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = unescape(re.sub(r'\s+', ' ', text)).strip()
    if length and len(text) > length:
        text = text[:length].rsplit(' ', 1)[0].rstrip('،,.:؛') + '…'
    return text


# Persian alphabet order; by codepoint پ چ ژ گ would sort after ی.
PERSIAN_ALPHABET = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
PERSIAN_ORDER = {letter: index for index, letter in enumerate(PERSIAN_ALPHABET)}
# Spelling variants, and marks readers don't type.
PERSIAN_EQUIVALENT = str.maketrans({
    'أ': 'ا', 'إ': 'ا', 'ٱ': 'ا', 'ء': 'ا',
    'ي': 'ی', 'ى': 'ی', 'ك': 'ک', 'ۀ': 'ه', 'ة': 'ه',
    '\u200c': ' ',                      # zero-width non-joiner
    '\u064b': '', '\u064c': '', '\u064d': '',   # tanwin
    '\u064e': '', '\u064f': '', '\u0650': '',   # short vowels
    '\u0651': '', '\u0652': '', '\u0654': '',
})


def glossary_key(title):
    """Sort key: Persian headings in Persian order, then Latin ones (ATP, DNA)."""

    text = str(title).translate(PERSIAN_EQUIVALENT).strip()
    if not text:
        return (2, ())
    persian = text[0] in PERSIAN_ORDER
    weights = tuple(PERSIAN_ORDER.get(ch, len(PERSIAN_ALPHABET) + ord(ch))
                    for ch in text.lower())
    return (0 if persian else 1, weights)


def glossary_groups(pages, script='fa'):
    """Glossary terms grouped by initial: `fa` by Persian title, `en` by English term."""

    terms = [p for p in pages if getattr(p, 'slug', '').startswith('glossary/')]
    groups = {}
    for term in terms:
        if script == 'fa':
            heading = str(term.title).translate(PERSIAN_EQUIVALENT).strip()
        else:
            heading = str(getattr(term, 'term', term.title)).strip()
        letter = heading[:1].upper() if heading else '؟'
        groups.setdefault(letter, []).append(term)

    def letter_key(letter):
        return glossary_key(letter)

    def term_key(term):
        return (glossary_key(term.title) if script == 'fa'
                else glossary_key(getattr(term, 'term', term.title)))

    return [(letter, sorted(items, key=term_key))
            for letter, items in sorted(groups.items(), key=lambda kv: letter_key(kv[0]))]


def to_json(value):
    """JSON with Persian kept as UTF-8 (a third the size of \\u escapes)."""

    return json.dumps(value, ensure_ascii=False)


DIGGING_DATA = re.compile(
    r'<section class="digging-data" id="([^"]+)"[^>]*>.*?<h2[^>]*>(.*?)</h2>', re.S)


def digging_data(articles):
    """Digging Data sections in book order: (article, anchor, title after the colon)."""

    found = []
    for article in sorted(articles, key=lambda a: a.source_path):
        match = DIGGING_DATA.search(article.content)
        if not match:
            continue
        heading = re.sub(r'<sup.*?</sup>|<[^>]+>', '', match.group(2), flags=re.S)
        title = unescape(heading).split(':', 1)[-1].strip()
        found.append((article, match.group(1), title))
    return found


JINJA_FILTERS = {
    'digging_data': digging_data,
    'glossary_groups': glossary_groups,
    'glossary_key': glossary_key,
    'persian_digits': persian_digits,
    'plain_text': plain_text,
    'to_json': to_json,
}

# English-only footnotes ("Lineage") get class footnote-latin so style.css can
# set them left-to-right; otherwise the ↩ lands before the term, not after.

PERSIAN_RANGE = re.compile(r'[؀-ۿ]')
# On the <li>, so the list number moves with the text.
FOOTNOTE_ENTRY = re.compile(r'(<li id="fn:[^"]*")(>)(.*?)(</li>)', re.S)


def latin_footnotes(content):
    """Add class="footnote-latin" to footnote entries with no Persian text."""

    def mark(match):
        open_tag, close_bracket, body, end = match.groups()
        # The backref's English title isn't visible text.
        visible = re.sub(r'<a class="footnote-backref".*?</a>', '', body, flags=re.S)
        if PERSIAN_RANGE.search(visible):
            return match.group(0)
        return f'{open_tag} class="footnote-latin"{close_bracket}{body}{end}'

    return FOOTNOTE_ENTRY.sub(mark, content)


def mark_latin_footnotes(instance):
    if instance._content and 'footnote-backref' in instance._content:
        instance._content = latin_footnotes(instance._content)


# Links leaving the site open in a new tab and get class external-link (⎋ in
# style.css). Page content only; templates such as the footer are untouched.
EXTERNAL_LINK = re.compile(r'<a href="https?://([^/"]*)[^"]*"(?![^>]*\btarget=)')
SITE_HOST = re.sub(r'^https?://(www\.)?', '', CANONICAL_SITEURL).split('/')[0]


def external_links_new_tab(instance):
    def mark(match):
        host = match.group(1).lower().removeprefix('www.')
        if host == SITE_HOST:
            return match.group(0)
        return match.group(0) + ' class="external-link" target="_blank" rel="noopener"'

    if instance._content:
        instance._content = EXTERNAL_LINK.sub(mark, instance._content)


def register():
    from pelican import signals
    signals.content_object_init.connect(mark_latin_footnotes)
    signals.content_object_init.connect(external_links_new_tab)


PLUGINS = [sys.modules[__name__]]

DIRECT_TEMPLATES = ('sitemap', 'search_index')
SITEMAP_SAVE_AS = 'sitemap.xml'
# Search index as .js rather than JSON, so it also loads from disk.
SEARCH_INDEX_SAVE_AS = 'search-index.js'
CATEGORY_SAVE_AS = ''
TAG_SAVE_AS = ''
AUTHOR_SAVE_AS = ''
