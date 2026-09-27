#!/usr/bin/env python3
"""Turn the scraped Berkeley glossary into content/glossary/*.md.

  python scripts/build_glossary.py [glossary/glossary.jsonl]

One file per term. Each keeps the English definition inside an "original"
block so it can be translated in place: replace the Persian placeholder above
it, leave the original for reference, and delete nothing.

Re-running it leaves any file that already exists alone, so translations are
never overwritten; pass --force to rebuild everything.
"""

import argparse
import ast
import json
import pathlib
import re
import sys

BERKELEY_GLOSSARY = 'https://evolution.berkeley.edu/glossary/'
OUT = pathlib.Path('content/glossary')


def chapter_slugs():
    """Berkeley page URL -> our Slug, so 'used in' links stay on our site."""
    out = {}
    for f in pathlib.Path('content/chapters').glob('*.md'):
        text = f.read_text(encoding='utf-8')
        source = re.search(r'^Source: (.+)$', text, re.M)
        title = re.search(r'^Title: (.+)$', text, re.M)
        if source and title:
            out[source.group(1).strip().rstrip('/')] = (f.name, title.group(1).strip())
    return out


def local_links(markdown, terms):
    """Point links at other glossary terms to our own pages."""
    def swap(match):
        text, url = match.group(1), match.group(2)
        slug = url.rstrip('/').rsplit('/', 1)[-1]
        if url.startswith(BERKELEY_GLOSSARY) and slug in terms:
            return f'[{text}]({{filename}}{slug}.md)'
        return match.group(0)

    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', swap, markdown)


def blocks_markdown(record, terms):
    """The entry's body, with its images hotlinked from evolution.berkeley.edu
    the way the chapters do it, at the size the original page shows them."""
    out = []
    for block in record.get('blocks', []):
        kind = block.get('type')
        if kind == 'image':
            if not block.get('src'):
                continue
            alt = block.get('alt') or block.get('caption') or record['term']
            size = ''
            if block.get('width') and block.get('height'):
                size = ('{: width="%s" height="%s" loading="lazy" }'
                        % (block['width'], block['height']))
            out.append(f'![{alt}]({block["src"]}){size}')
            if block.get('caption'):
                out.append(f'<div class="caption" markdown="1">{block["caption"]}</div>')
        elif kind == 'list':
            items = block.get('items') or []
            # The scraper sometimes stored the list as its Python repr.
            if isinstance(items, str):
                items = ast.literal_eval(items)
            marker = '1.' if block.get('ordered') else '-'
            out.append('\n'.join(f'{marker} {local_links(item, terms)}' for item in items))
        elif kind == 'heading':
            # The small headings on these pages hold labels and photo credits.
            level = block.get('level', 6)
            text = ' '.join(block['text'].split())
            out.append(f'{"#" * level} {text}')
        elif block.get('markdown') or block.get('text'):
            out.append(local_links(block.get('markdown') or block['text'], terms))
    if not out:
        out.append(local_links(record.get('definition_markdown') or record['definition'], terms))
    return '\n\n'.join(out)


def page(record, terms, chapters):
    slug = record['slug']
    term = record['term']
    body = blocks_markdown(record, terms)

    used = []
    for ref in record.get('used_in_evo101', []):
        found = chapters.get(ref['url'].rstrip('/'))
        if found:
            used.append(f'- [{found[1]}]({{filename}}../chapters/{found[0]})')

    # The Persian translation first, then the English it came from. Title is
    # the Persian term once translated; Term keeps the English one.
    lines = [
        f'Title: {term}',
        'Date: 2025-11-06 00:00',
        f'Slug: glossary/{slug}',
        f'Term: {term}',
        f'Source: {record["url"]}',
        f'Source_title: {term}',
        'Author: mortezagk',
        'Translated: no',
        '',
        '<div class="term-translation" markdown="1">',
        '',
        '</div>',
        '',
        '<div class="term-original" lang="en" dir="ltr" markdown="1">',
        body,
        '</div>',
    ]
    if used:
        lines += ['', '## در این صفحه‌ها آمده است', ''] + used
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', default='glossary/glossary.jsonl')
    parser.add_argument('--force', action='store_true',
                        help='rewrite files that already exist (loses translations)')
    args = parser.parse_args()

    path = pathlib.Path(args.source)
    if not path.is_file():
        sys.exit(f'Glossary data not found: {path}')

    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    terms = {r['slug'] for r in records}
    chapters = chapter_slugs()

    OUT.mkdir(parents=True, exist_ok=True)
    written = kept = 0
    for record in records:
        target = OUT / f'{record["slug"]}.md'
        if target.exists() and not args.force:
            kept += 1
            continue
        target.write_text(page(record, terms, chapters), encoding='utf-8')
        written += 1

    print(f'{written} written, {kept} left alone, {len(records)} terms in total.')


if __name__ == '__main__':
    main()
