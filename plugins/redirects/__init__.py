"""Write redirect stubs for articles that moved.

An article with ``Redirect_from: old/path.html`` metadata gets a small HTML
page at that old path that forwards visitors to the article's current URL.
"""

import html
import os
import posixpath

from pelican import signals

TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<meta name="robots" content="noindex">
</head>
<body>
<p>این صفحه منتقل شده است: <a href="{target}">{title}</a></p>
</body>
</html>
"""


def write_redirects(generator, writer):
    output_path = generator.output_path
    siteurl = generator.settings.get('SITEURL', '')
    relative = generator.settings.get('RELATIVE_URLS', False)
    for article in generator.articles:
        old_paths = getattr(article, 'redirect_from', None)
        if not old_paths:
            continue
        for old in old_paths.split(','):
            old = old.strip().lstrip('/')
            if not old:
                continue
            if relative:
                target = posixpath.relpath(article.url or '.', posixpath.dirname(old) or '.')
                if article.url.endswith('/') and not target.endswith('/'):
                    target += '/'
            else:
                target = f'{siteurl}/{article.url}'
            dest = os.path.join(output_path, old)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'w', encoding='utf-8') as fh:
                fh.write(TEMPLATE.format(title=html.escape(article.title),
                                         target=html.escape(target, quote=True)))


def register():
    signals.article_writer_finalized.connect(write_redirects)
