#!/usr/bin/env python3
"""Check the built site for broken links.

  python scripts/check_links.py [_build]           # internal links
  python scripts/check_links.py --images [_build]  # external images

* By default, internal links and images (relative href/src) must point at a
  file that exists in the build. No network needed; takes a second or two.
* With --images, external images (<img src="http...">, hotlinked from
  evolution.berkeley.edu) must load instead: HTTP 200 with an image content
  type. Each URL is tried twice before it counts as broken.

Exits with status 1 and lists every broken link if anything fails.
"""

import argparse
import concurrent.futures
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

# Browser-like headers: some servers stall or refuse requests that look like
# bots, which made this check hang for minutes on GitHub's runners.
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/140.0 Safari/537.36 '
                   'evolution101-link-check'),
    'Accept': 'image/avif,image/webp,image/png,image/*;q=0.8,*/*;q=0.5',
    'Referer': 'https://evolution101.ir/',
}
ATTEMPTS = 2
TIMEOUT = 15
WORKERS = 16


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
        request = urllib.request.Request(url, headers=HEADERS)
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
        if attempt + 1 < ATTEMPTS:
            time.sleep(3)
    return error


def main():
    parser = argparse.ArgumentParser(description='Check the built site for broken links.')
    parser.add_argument('build', nargs='?', default='_build')
    parser.add_argument('--images', action='store_true',
                        help='check external images over the network instead of internal links')
    args = parser.parse_args()
    root = Path(args.build).resolve()
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
            if args.images:
                continue
            error = check_internal(page, url, root)
            if error:
                problems.append((page.relative_to(root), url, error))

    if args.images:
        total = len(external_images)
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {pool.submit(check_image, url): url for url in external_images}
            for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
                url, error = futures[future], future.result()
                print(f'[{done}/{total}] {"FAIL" if error else "ok  "} {url}'
                      + (f' ({error})' if error else ''), flush=True)
                if error:
                    for page in sorted(external_images[url]):
                        problems.append((page, url, error))
        print(f'Checked {total} external images on {len(pages)} pages.')
    else:
        print(f'Checked internal links on {len(pages)} pages.')
    if problems:
        print(f'\n{len(problems)} broken link(s):')
        for page, url, error in sorted(problems, key=lambda p: (str(p[0]), p[1])):
            print(f'  {page}: {url}\n      {error}')
        sys.exit(1)
    print('No broken links.')


if __name__ == '__main__':
    main()
