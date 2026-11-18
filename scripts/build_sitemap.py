#!/usr/bin/env python3
"""Construit le sitemap à partir des URL canoniques des pages publiques."""
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
NAMESPACE = 'http://www.sitemaps.org/schemas/sitemap/0.9'


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.excluded = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a.get('href')
        if tag == 'meta' and a.get('name', '').lower() == 'robots':
            self.excluded = bool({'noindex', 'none'} & set(a.get('content', '').lower().replace(',', ' ').split()))


def build():
    ET.register_namespace('', NAMESPACE)
    root = ET.Element(f'{{{NAMESPACE}}}urlset')
    for path in sorted(ROOT.rglob('*.html')):
        if any(part.startswith('.') or part == 'preview' for part in path.relative_to(ROOT).parts):
            continue
        metadata = Metadata()
        metadata.feed(path.read_text(encoding='utf-8'))
        if metadata.canonical and not metadata.excluded:
            entry = ET.SubElement(root, f'{{{NAMESPACE}}}url')
            ET.SubElement(entry, f'{{{NAMESPACE}}}loc').text = metadata.canonical
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    build()
