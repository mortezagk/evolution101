#!/usr/bin/env python3
"""Check the built site for broken links.

  python scripts/check_links.py [_build]

* Internal links and images (relative href/src) must point at a file that
  exists in the build.
* External images (<img src="http...">) must load: HTTP 200 with an image
  content type. Each URL is tried a few times before it counts as broken.

Exits with status 1 and lists every broken link if anything fails.
"""

import concurrent.futures
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = 'evolution101-link-check (+https://github.com/mortezagk/evolution101)'
ATTEMPTS = 3
TIMEOUT = 20


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []  # (tag, attribute value)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ('href', 'src'):
            if attrs.get(name):
                self.links.append((tag, attrs[name]))


def is_external(url):
    return url.startswith(('http://', 'https://', '//'))


def check_internal(page, url, root):
    path = url.split('#', 1)[0].split('?', 1)[0]
    if not path:
        return None  # same-page anchor
    target = (root / path.lstrip('/')) if path.startswith('/') else (page.parent / path)
    target = target.resolve()
    if target.is_dir():
        target = target / 'index.html'
    return None if target.is_file() else 'file not found in build'


def check_image(url):
    if url.startswith('//'):
        url = 'https:' + url
    error = None
    for attempt in range(ATTEMPTS):
        request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                ctype = response.headers.get('Content-Type', '')
                response.read(1024)
                if response.status == 200 and ctype.startswith('image/'):
                    return None
                error = f'HTTP {response.status}, Content-Type {ctype or "missing"}'
                if response.status == 200:
                    return error  # served, but not an image: retrying won't help
        except urllib.error.HTTPError as exc:
            error = f'HTTP {exc.code}'
            if exc.code in (403, 404, 410):
                return error
        except Exception as exc:  # timeouts, DNS, TLS, connection resets
            error = f'{type(exc).__name__}: {exc}'
        time.sleep(2 * (attempt + 1))
    return error


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '_build').resolve()
    if not root.is_dir():
        sys.exit(f'Build directory not found: {root}')

    problems = []
    external_images = {}  # url -> pages using it
    pages = sorted(root.rglob('*.html'))
    for page in pages:
        collector = LinkCollector()
        collector.feed(page.read_text(encoding='utf-8'))
        for tag, url in collector.links:
            if url.startswith(('mailto:', 'tel:', 'data:', 'javascript:', '#')):
                continue
            if is_external(url):
                if tag == 'img':
                    external_images.setdefault(url, set()).add(page.relative_to(root))
                continue
            error = check_internal(page, url, root)
            if error:
                problems.append((page.relative_to(root), url, error))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(external_images, pool.map(check_image, external_images)))
    for url, error in results.items():
        if error:
            for page in sorted(external_images[url]):
                problems.append((page, url, error))

    print(f'Checked {len(pages)} pages and {len(external_images)} external images.')
    if problems:
        print(f'\n{len(problems)} broken link(s):')
        for page, url, error in sorted(problems, key=lambda p: (str(p[0]), p[1])):
            print(f'  {page}: {url}\n      {error}')
        sys.exit(1)
    print('No broken links.')


if __name__ == '__main__':
    main()
