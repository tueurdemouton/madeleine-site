#!/usr/bin/env python3
"""Contrôle hors réseau des protections et des liens du site statique."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
ERRORS = []
REMOTE_LINKS = {'apps.apple.com', 'testflight.apple.com', 'www.cnil.fr'}


def check(ok, where, message):
    if not ok:
        ERRORS.append(f'{where}: {message}')


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.policy = None
        self.headings = 0
        self.ids = set()
        self.fragments = []
        self.remote_referrers = False
        self.resource_seen = False
        self.script_open = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        where = f'{self.path.name}:{self.getpos()[0]}'
        check(not any(k.startswith('on') or k == 'style' for k in a), where,
              'code ou style intégré au HTML interdit')
        if 'id' in a:
            check(a['id'] not in self.ids, where, 'identifiant HTML dupliqué')
            self.ids.add(a['id'])
        if tag == 'h1':
            self.headings += 1
        check(tag not in {'form', 'iframe', 'object', 'embed', 'base'}, where,
              f'élément {tag} interdit sur le site public')
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'content-security-policy':
            check(not self.resource_seen, where, 'CSP placée après une ressource')
            check(self.policy is None, where, 'plusieurs CSP inattendues')
            self.policy = dict((bits[0], bits[1:]) for chunk in a.get('content', '').split(';') if (bits := chunk.split()))
        if tag == 'meta' and a.get('name') == 'referrer':
            self.remote_referrers = a.get('content') == 'no-referrer'
        if tag == 'script':
            check(bool(a.get('src')), where, 'script sans fichier source')
            self.script_open = True
        if tag in {'script', 'img', 'link'}:
            self.resource_seen = True
        if a.get('target') == '_blank':
            check({'noopener', 'noreferrer'} <= set(a.get('rel', '').split()), where,
                  'nouvel onglet externe non isolé')
        for key in ['href', 'src']:
            if key not in a:
                continue
            url = urlsplit(a[key])
            resource = key == 'src' or (tag == 'link' and a.get('rel') != 'canonical')
            if resource:
                check(not url.scheme and not url.netloc, where, 'ressource externe interdite')
            if url.scheme:
                check(url.scheme in {'https', 'mailto'}, where, 'protocole non autorisé')
                if tag == 'a' and url.scheme == 'https':
                    check(url.hostname in REMOTE_LINKS, where, 'destination externe à vérifier')
            elif url.netloc:
                check(False, where, 'URL sans protocole interdite')
            elif url.path:
                target = (self.path.parent / unquote(url.path)).resolve()
                check(ROOT in target.parents and target.is_file(), where,
                      f'ressource locale absente ou chemin hors du site : {url.path}')
            elif url.fragment:
                self.fragments.append((where, unquote(url.fragment)))

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script_open = False

    def handle_data(self, data):
        if self.script_open:
            check(not data.strip(), self.path.name, 'script intégré au HTML interdit')

    def verify(self):
        check(self.headings == 1, self.path.name, 'un seul titre principal requis')
        check(self.remote_referrers, self.path.name, 'protection du référent absente')
        check(self.policy is not None, self.path.name, 'CSP absente')
        for directive in ['default-src', 'connect-src', 'object-src', 'base-uri', 'form-action', 'frame-src']:
            check((self.policy or {}).get(directive) == ["'none'"], self.path.name,
                  f'{directive} doit bloquer tout accès')
        for directive in ['style-src', 'font-src', 'img-src']:
            check((self.policy or {}).get(directive) == ["'self'"], self.path.name,
                  f'{directive} doit rester local')
        expected = ["'self'"] if self.path.name == 'telecharger.html' else ["'none'"]
        check((self.policy or {}).get('script-src') == expected, self.path.name, 'scripts trop permissifs')
        for where, fragment in self.fragments:
            check(fragment in self.ids, where, 'ancre absente : ' + fragment)


for path in sorted(ROOT.glob('*.html')):
    page = Page(path)
    page.feed(path.read_text())
    page.verify()
css = (ROOT / 'style.css').read_text()
check(not re.search(r'@import|url\(\s*[\'"]?(?:https?:|//|data:)', css, re.I), 'style.css', 'ressource CSS externe interdite')
check((ROOT / '.nojekyll').exists(), '.nojekyll', 'publication statique non déclarée')
check((ROOT / 'CNAME').read_text().strip() == 'madeleine-de-gout.com', 'CNAME', 'domaine modifié')
check((ROOT / 'fonts/OFL.txt').exists(), 'police', 'licence absente')
if ERRORS:
    print('\n'.join(ERRORS), file=sys.stderr)
    sys.exit(1)
print('OK : CSP, ressources locales, liens, ancres et structure des pages.')
