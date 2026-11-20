#!/usr/bin/env python3
"""Contrôle hors réseau des protections et des liens du site statique."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import re
import sys
import json
import hashlib
import base64

ROOT = Path(__file__).resolve().parent.parent
ERRORS = []
# Sources officielles relues pour les comparatifs, pas de domaine générique.
REMOTE_LINKS = {
    'apps.apple.com', 'testflight.apple.com', 'www.cnil.fr', 'jow.com',
    'www.carrefour.fr', 'www.hellofresh.fr', 'www.quitoque.fr', 'lescommis.com',
    'www.recettesetcabas.com', 'samsungfood.com', 'www.paprikaapp.com',
    'paprikaapp.zendesk.com', 'www.plantoeat.com', 'www.anylist.com',
    'www.getbring.com', 'www.marmiton.org', 'www.vorwerk.com',
    'support-france.vorwerk.com', 'www.mealime.com',
}
ORIGIN = 'https://madeleine-de-gout.com'


def local_target(path, url_path):
    target = (ROOT / unquote(url_path).lstrip('/') if url_path.startswith('/')
              else path.parent / unquote(url_path)).resolve()
    if target.is_dir():
        target = target / 'index.html'
    return target


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
        self.robots = set()
        self.resource_seen = False
        self.script_open = False
        self.scripts = []
        self.title = ''
        self.in_title = False
        self.description = None
        self.canonical = None
        self.language = None
        self.viewport = None
        self.script_kind = None
        self.script_content = []
        self.jsonld = []
        self.visible_text = []
        self.tables = 0
        self.table_captions = 0
        self.table_headers = 0
        self.og = {}

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
        if tag == 'html':
            self.language = a.get('lang')
        if tag == 'title':
            self.in_title = True
        if tag == 'meta' and a.get('name') == 'description':
            check(self.description is None, where, 'description dupliquée')
            self.description = a.get('content', '')
        if tag == 'meta' and a.get('name') == 'viewport':
            self.viewport = a.get('content', '')
        if tag == 'meta' and a.get('property', '').startswith('og:'):
            self.og[a['property']] = a.get('content', '')
        if tag == 'table':
            self.tables += 1
        if tag == 'caption':
            self.table_captions += 1
        if tag == 'th':
            self.table_headers += 1
            check(a.get('scope') in {'col', 'row'}, where, 'portée d’en-tête de tableau absente')
        if tag == 'link' and a.get('rel') == 'canonical':
            check(self.canonical is None, where, 'URL canonique dupliquée')
            self.canonical = a.get('href')
        check(tag not in {'form', 'iframe', 'object', 'embed', 'base'}, where,
              f'élément {tag} interdit sur le site public')
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'content-security-policy':
            check(not self.resource_seen, where, 'CSP placée après une ressource')
            check(self.policy is None, where, 'plusieurs CSP inattendues')
            self.policy = dict((bits[0], bits[1:]) for chunk in a.get('content', '').split(';') if (bits := chunk.split()))
        if tag == 'meta' and a.get('name', '').lower() == 'robots':
            self.robots.update(item.strip().lower() for item in a.get('content', '').split(','))
        if tag == 'meta' and a.get('name') == 'referrer':
            self.remote_referrers = a.get('content') == 'no-referrer'
        if tag == 'script':
            self.script_kind = a.get('type')
            self.script_content = []
            if self.script_kind != 'application/ld+json':
                self.scripts.append(Path(urlsplit(a.get('src', '')).path).name)
                check(bool(a.get('src')), where, 'script exécutable sans fichier source')
            else:
                check(not a.get('src'), where, 'JSON-LD externe interdit')
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
                target = local_target(self.path, url.path)
                check(ROOT in target.parents and target.is_file(), where,
                      f'ressource locale absente ou chemin hors du site : {url.path}')
                if url.fragment:
                    self.fragments.append((where, target, unquote(url.fragment)))
            elif url.fragment:
                self.fragments.append((where, self.path, unquote(url.fragment)))

    def handle_endtag(self, tag):
        if tag == 'script':
            if self.script_kind == 'application/ld+json':
                self.jsonld.append(''.join(self.script_content))
            self.script_open = False
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.script_open:
            if self.script_kind == 'application/ld+json':
                self.script_content.append(data)
            else:
                check(not data.strip(), self.path.name, 'script exécutable intégré au HTML interdit')
        else:
            self.visible_text.append(data)
        if self.in_title:
            self.title += data

    def verify(self):
        check(self.headings == 1, self.path.name, 'un seul titre principal requis')
        check(self.language == 'fr', self.path.name, 'langue française absente')
        check('width=device-width' in (self.viewport or ''), self.path.name, 'viewport mobile absent')
        check(bool(self.title.strip()), self.path.name, 'titre de page absent')
        check(bool(self.description), self.path.name, 'description absente')
        relative = self.path.relative_to(ROOT).as_posix()
        expected_url = ORIGIN + '/' + (relative[:-10] if relative.endswith('index.html') else relative)
        check(self.canonical == expected_url, relative, 'URL canonique absente ou incohérente')
        check(not ({'noindex', 'none', 'nofollow', 'noimageindex'} & self.robots), self.path.name,
              'consigne de non-référencement : le site doit être référencé')
        check(self.remote_referrers, self.path.name, 'protection du référent absente')
        check(self.policy is not None, self.path.name, 'CSP absente')
        for directive in ['default-src', 'connect-src', 'object-src', 'base-uri', 'form-action', 'frame-src']:
            check((self.policy or {}).get(directive) == ["'none'"], self.path.name,
                  f'{directive} doit bloquer tout accès')
        for directive in ['style-src', 'font-src', 'img-src']:
            check((self.policy or {}).get(directive) == ["'self'"], self.path.name,
                  f'{directive} doit rester local')
        expected_scripts = {
            'index.html': ['effects.js', 'tour.js'],
            'telecharger.html': ['download.js', 'effects.js'],
            'comparatifs/index.html': ['comparisons.js'],
        }
        allowed = expected_scripts.get(relative, [])
        check(self.scripts == allowed, self.path.name, 'liste des scripts locaux inattendue')
        hashes = ["'sha256-" + base64.b64encode(hashlib.sha256(block.encode()).digest()).decode() + "'" for block in self.jsonld]
        expected = (["'self'"] if allowed else []) + hashes
        if not expected:
            expected = ["'none'"]
        check((self.policy or {}).get('script-src') == expected, self.path.name, 'scripts trop permissifs')
        check((self.policy or {}).get('script-src-attr') == ["'none'"], relative, 'gestionnaires inline interdits')
        check((self.policy or {}).get('style-src-attr') == ["'none'"], relative, 'styles inline interdits')
        for block in self.jsonld:
            try:
                data = json.loads(block)
                check(data.get('@context') == 'https://schema.org', relative, 'contexte JSON-LD invalide')
                graph = data.get('@graph', [])
                check(bool(graph), relative, 'graphe JSON-LD vide')
                visible = ' '.join(' '.join(self.visible_text).split())
                for entity in graph:
                    check(entity.get('@type') not in {'Review', 'AggregateRating'}, relative, 'avis ou note non justifiés')
                    if entity.get('@type') == 'FAQPage':
                        for question in entity.get('mainEntity', []):
                            answer = question.get('acceptedAnswer', {}).get('text', '')
                            check(bool(question.get('name')) and question['name'] in visible, relative, 'question structurée absente du texte')
                            check(bool(answer) and answer in visible, relative, 'réponse structurée absente du texte')
                    if entity.get('@type') == 'Article':
                        check(entity.get('mainEntityOfPage') == self.canonical, relative, 'article structuré sans URL cohérente')
                        for field in ['headline', 'datePublished', 'dateModified', 'author', 'publisher']:
                            check(bool(entity.get(field)), relative, f'article structuré sans {field}')
                    main_entity = entity.get('mainEntity', {})
                    if entity.get('@type') == 'ItemList' or (isinstance(main_entity, dict) and main_entity.get('@type') == 'ItemList'):
                        listing = entity if entity.get('@type') == 'ItemList' else main_entity
                        entries = listing.get('itemListElement', [])
                        check(listing.get('numberOfItems') == len(entries), relative, 'nombre de comparatifs incohérent')
                        for entry in entries:
                            target = local_target(self.path, urlsplit(entry.get('url', '')).path)
                            check(target.is_file(), relative, 'comparatif structuré sans page réelle')
            except (ValueError, TypeError, AttributeError) as error:
                check(False, relative, 'JSON-LD invalide : ' + str(error))
        if relative.startswith('comparatifs/') and '/madeleine-vs-' in '/' + relative:
            check(self.tables == self.table_captions == 1 and self.table_headers >= 3,
                  relative, 'tableau comparatif accessible absent')
            check(len(self.jsonld) == 1, relative, 'données structurées du comparatif absentes')
            for required in ['reponse', 'tableau', 'choisir', 'cas-pratique', 'questions', 'sources']:
                check(required in self.ids, relative, f'section du comparatif absente : {required}')
        check(self.og.get('og:url') == self.canonical, relative, 'URL de partage incohérente')
        check(bool(self.og.get('og:title')) and bool(self.og.get('og:description')), relative, 'aperçu de partage incomplet')
        for where, target, fragment in self.fragments:
            check(target in PAGES and fragment in PAGES[target].ids, where,
                  'ancre absente : ' + fragment)


PAGES = {}
for path in sorted(ROOT.rglob('*.html')):
    if any(part.startswith('.') or part == 'preview' for part in path.relative_to(ROOT).parts):
        continue
    page = Page(path)
    page.feed(path.read_text(encoding='utf-8'))
    PAGES[path] = page
for page in PAGES.values():
    page.verify()
titles = [page.title.strip() for page in PAGES.values()]
check(len(titles) == len(set(titles)), 'titres', 'plusieurs pages ont le même titre')
descriptions = [page.description for page in PAGES.values()]
check(len(descriptions) == len(set(descriptions)), 'descriptions', 'plusieurs pages ont la même description')
try:
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    locations = [node.text for node in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    canonical_urls = {page.canonical for page in PAGES.values() if page.canonical}
    check(set(locations) == canonical_urls and len(locations) == len(canonical_urls),
          'sitemap.xml', 'le sitemap doit contenir exactement les URL canoniques publiques')
except (OSError, ET.ParseError) as error:
    check(False, 'sitemap.xml', str(error))
try:
    robots = (ROOT / 'robots.txt').read_text()
    check('Sitemap: ' + ORIGIN + '/sitemap.xml' in robots, 'robots.txt', 'sitemap non déclaré')
    check(not re.search(r'^\s*Disallow\s*:\s*/\s*$', robots, re.M | re.I),
          'robots.txt', 'exploration du site bloquée')
except OSError as error:
    check(False, 'robots.txt', str(error))
for path in ROOT.glob('*.css'):
    css = path.read_text()
    check(not re.search(r'@import|url\(\s*[\'"]?(?:https?:|//|data:)', css, re.I), path.name, 'ressource CSS externe interdite')
check((ROOT / '.nojekyll').exists(), '.nojekyll', 'publication statique non déclarée')
check((ROOT / 'CNAME').read_text().strip() == 'madeleine-de-gout.com', 'CNAME', 'domaine modifié')
check((ROOT / 'fonts/OFL.txt').exists(), 'police', 'licence absente')
planning = ROOT / 'guides/organiser-repas-famille-gouts-differents/planning-repas-famille.pdf'
check(planning.is_file() and planning.read_bytes().startswith(b'%PDF-'),
      'planning-repas-famille.pdf', 'planning PDF absent ou invalide')
if ERRORS:
    print('\n'.join(ERRORS), file=sys.stderr)
    sys.exit(1)
print('OK : référencement, CSP, ressources locales, liens, ancres et structure des pages.')
