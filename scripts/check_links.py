#!/usr/bin/env python3
"""Check the built site for broken links.

  python scripts/check_links.py [_build]           # internal links
  python scripts/check_links.py --images [_build]  # external images

* By default, internal links and images (relative href/src) must point at a
  file that exists in the build. No network needed; takes a second or two.
* With --images, external images (<img src="http...">, hotlinked from
  evolution.berkeley.edu) are checked instead. An image is broken only when
  its server answers and says so: 404/410 (or another 4xx), or a reply that
  isn't an image. A server that can't be reached (timeouts, refused or
  dropped connections, 403/429/5xx) proves nothing about the image, so that
  is only a warning: Berkeley's firewall drops connections from some GitHub
  runners. After a few such failures in a row with no success, the rest of
  that server's images are skipped rather than waited on.

Exits with status 1 and lists every broken link if anything is broken.
"""

import argparse
import concurrent.futures
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

# Browser-like headers, so the request is treated like the page's own image
# requests.
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/140.0 Safari/537.36 '
                   'evolution101-link-check'),
    'Accept': 'image/avif,image/webp,image/png,image/*;q=0.8,*/*;q=0.5',
    'Referer': 'https://evolution101.ir/',
}
ATTEMPTS = 2
TIMEOUT = 15
WORKERS = 4        # gentle on the image server
GIVE_UP_AFTER = 4  # unreachable in a row, with no success, before skipping a host

OK, BROKEN, UNREACHABLE, SKIPPED = 'ok', 'broken', 'unreachable', 'skipped'


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


class HostTracker:
    """Notices when a server isn't answering at all, so we stop waiting on it."""

    def __init__(self):
        self.lock = threading.Lock()
        self.reached = set()
        self.failures = {}

    def given_up(self, host):
        with self.lock:
            return host not in self.reached and self.failures.get(host, 0) >= GIVE_UP_AFTER

    def record(self, host, status):
        with self.lock:
            if status == UNREACHABLE:
                self.failures[host] = self.failures.get(host, 0) + 1
            else:
                self.reached.add(host)


def fetch_image(url):
    """Return (status, detail) for one image URL."""
    detail = None
    for attempt in range(ATTEMPTS):
        request = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                ctype = response.headers.get('Content-Type', '')
                response.read(1024)
                if ctype.startswith('image/'):
                    return OK, None
                return BROKEN, f'HTTP {response.status}, Content-Type {ctype or "missing"}'
        except urllib.error.HTTPError as exc:
            detail = f'HTTP {exc.code}'
            # 403 is usually a firewall, 408/429 rate limiting: not the image.
            if 400 <= exc.code < 500 and exc.code not in (403, 408, 429):
                return BROKEN, detail
        except Exception as exc:  # timeouts, DNS, TLS, refused/dropped connections
            detail = f'{type(exc).__name__}: {exc}'
        if attempt + 1 < ATTEMPTS:
            time.sleep(3)
    return UNREACHABLE, detail


def check_image(url, hosts):
    if url.startswith('//'):
        url = 'https:' + url
    host = urlsplit(url).netloc
    if hosts.given_up(host):
        return SKIPPED, f'{host} is not answering'
    status, detail = fetch_image(url)
    hosts.record(host, status)
    return status, detail


def warn(message):
    # A yellow annotation on GitHub; a plain line anywhere else.
    prefix = '::warning::' if os.environ.get('GITHUB_ACTIONS') else 'Warning: '
    print(prefix + message, flush=True)


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
        hosts = HostTracker()
        counts = {OK: 0, BROKEN: 0, UNREACHABLE: 0, SKIPPED: 0}
        not_checked = {}  # host -> number of images
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {pool.submit(check_image, url, hosts): url for url in external_images}
            for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
                url = futures[future]
                status, detail = future.result()
                counts[status] += 1
                print(f'[{done}/{total}] {status:<11} {url}'
                      + (f' ({detail})' if detail else ''), flush=True)
                if status == BROKEN:
                    for page in sorted(external_images[url]):
                        problems.append((page, url, detail))
                elif status in (UNREACHABLE, SKIPPED):
                    host = urlsplit(url).netloc
                    not_checked[host] = not_checked.get(host, 0) + 1
        print(f'External images on {len(pages)} pages: {counts[OK]} ok, '
              f'{counts[BROKEN]} broken, {counts[UNREACHABLE] + counts[SKIPPED]} not checked.')
        for host, n in sorted(not_checked.items()):
            warn(f'{n} image(s) on {host} were not checked: the server did not answer '
                 'or refused us. That does not mean they are broken; run the check '
                 'again later or from another network.')
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
