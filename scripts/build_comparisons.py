#!/usr/bin/env python3
"""Génère les comparatifs statiques depuis les faits relus dans comparisons.json.

La date est éditoriale : ne la changer qu'après une nouvelle vérification des
sources. Le JSON-LD est autorisé par son empreinte CSP, sans unsafe-inline.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://madeleine-de-gout.com'
CHECKED = '2026-11-20'
DISPLAY_DATE = '20 novembre 2026'
CATEGORIES = {
    'applications': 'Applications de menus',
    'box': 'Box et paniers à cuisiner',
    'courses': 'Listes de courses',
    'recettes': 'Recettes et cuisine guidée',
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def header(active: str = 'comparatifs') -> str:
    links = [('/', 'L’application', 'application'), ('/guides/', 'Guides & menus', 'guides'), ('/comparatifs/', 'Comparatifs', 'comparatifs')]
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if key == active else '') + f'>{esc(label)}</a>' for url, label, key in links)
    return f'''<a class="skip-link" href="#contenu">Aller au contenu</a>
  <header class="site-header"><a class="brand" href="/" aria-label="Madeleine de Goût, accueil"><img src="/images/logo.webp" alt="Madeleine de Goût" width="738" height="160"></a><nav class="site-nav" aria-label="Navigation principale">{nav}</nav><a class="button button-small header-cta" href="/telecharger.html">Essayer la bêta</a></header>'''


def footer() -> str:
    return '''<footer class="site-footer"><a href="/">L’application</a><a href="/guides/">Guides &amp; menus</a><a href="/comparatifs/">Comparatifs</a><a href="/comparatifs/methode/">Notre méthode</a><a href="mailto:paul@madeleine-de-gout.com">Nous écrire</a><a href="/confidentialite.html">Confidentialité</a><span>© 2026 Madeleine de Goût</span></footer>'''


def breadcrumb(items: list[tuple[str, str]]) -> tuple[str, dict]:
    trail = []
    structured = []
    for position, (label, url) in enumerate(items, 1):
        trail.append(f'<li><a href="{url}">{esc(label)}</a></li>' if position < len(items) else f'<li aria-current="page">{esc(label)}</li>')
        structured.append({'@type': 'ListItem', 'position': position, 'name': label, 'item': ORIGIN + url})
    return '<nav class="breadcrumbs" aria-label="Fil d’Ariane"><ol>' + ''.join(trail) + '</ol></nav>', {'@type': 'BreadcrumbList', 'itemListElement': structured}


def document(title: str, description: str, path: str, body: str, graph: list[dict], script: str | None = None, article: bool = False) -> str:
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    digest = base64.b64encode(hashlib.sha256(data.encode()).digest()).decode()
    script_policy = ("'self' " if script else '') + f"'sha256-{digest}'"
    policy = f"default-src 'none'; script-src {script_policy}; script-src-attr 'none'; style-src 'self'; style-src-attr 'none'; font-src 'self'; img-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-src 'none'; upgrade-insecure-requests"
    return f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="{policy}">
  <meta name="referrer" content="no-referrer">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#fffdf9">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{ORIGIN}{path}">
  <meta property="og:type" content="{'article' if article else 'website'}">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{ORIGIN}{path}">
  <meta property="og:site_name" content="Madeleine de Goût">
  <meta property="og:image" content="{ORIGIN}/images/partage.png">
  <meta property="og:image:alt" content="Le logo et la mascotte de Madeleine de Goût">
  <meta name="twitter:card" content="summary_large_image">
  {f'<meta property="article:published_time" content="{CHECKED}"><meta property="article:modified_time" content="{CHECKED}">' if article else ''}
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" type="image/png" sizes="192x192" href="/images/icon-192.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="stylesheet" href="/style.css?v=20261120">
  <link rel="stylesheet" href="/design.css?v=20261120">
  {f'<script src="/{script}?v=20261120" defer></script>' if script else ''}
  <script type="application/ld+json">{data}</script>
</head>
<body>{header()}{body}{footer()}</body>
</html>
'''.replace('\n  \n', '\n\n')


def article_schema(title: str, description: str, path: str, sources: list[list[str]]) -> dict:
    return {'@type': 'Article', '@id': ORIGIN + path + '#article', 'headline': title,
            'description': description, 'mainEntityOfPage': ORIGIN + path,
            'inLanguage': 'fr-FR', 'datePublished': CHECKED, 'dateModified': CHECKED,
            'image': ORIGIN + '/images/partage.png',
            'author': {'@type': 'Organization', 'name': 'Madeleine de Goût', 'url': ORIGIN + '/'},
            'publisher': {'@type': 'Organization', 'name': 'Madeleine de Goût', 'url': ORIGIN + '/'},
            'citation': [url for _, url in sources]}


def comparison_card(item: dict, searchable: bool = False) -> str:
    attributes = f' data-comparison data-category="{item["category"]}"' if searchable else ''
    return f'''<article class="comparison-card"{attributes}>
      <p class="card-category">{esc(item['label'])}</p>
      <p class="competitor-name">{esc(item['mark'])}</p>
      <h3><a href="/comparatifs/madeleine-vs-{item['slug']}/">Madeleine vs {esc(item['name'])}</a></h3>
      <p>{esc(item['angle'])}</p><span class="card-read" aria-hidden="true">Lire le comparatif</span>
    </article>'''


def build_detail(item: dict, all_items: list[dict]) -> None:
    name = esc(item['name'])
    path = f'/comparatifs/madeleine-vs-{item["slug"]}/'
    title = f'Madeleine de Goût vs {item["name"]} : quel choix en 2026 ?'
    if item['slug'] == 'mealime':
        title = 'Alternative à Mealime après son arrêt : Madeleine de Goût'
    crumbs, crumbs_schema = breadcrumb([('Accueil', '/'), ('Comparatifs', '/comparatifs/'), (f'Madeleine vs {item["name"]}', path)])
    rows = ''.join(f'<tr><th scope="row">{esc(label)}</th><td>{esc(ours)}</td><td>{esc(theirs)} <a class="source-ref" href="#source-{source}" aria-label="Voir la source {source}">[{source}]</a></td></tr>' for label, ours, theirs, source in item['rows'])
    sources = ''.join(f'<li id="source-{i}"><a href="{esc(url)}" rel="noopener noreferrer">{esc(label)}</a><span>Consulté le {DISPLAY_DATE}.</span></li>' for i, (label, url) in enumerate(item['sources'], 1))
    faq = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in item['faq'])
    related = [other for other in all_items if other['slug'] != item['slug'] and other['category'] == item['category']]
    related += [other for other in all_items if other['slug'] != item['slug'] and other not in related]
    body = f'''<main id="contenu" class="comparison-page">
    {crumbs}
    <article>
      <header class="comparison-hero"><p class="eyebrow">Le bon outil pour votre quotidien</p><h1>Madeleine de Goût <span>vs {name}.</span></h1><p class="lead">{esc(item['angle'])}</p><p class="article-meta">Par Madeleine de Goût · Vérifié le <time datetime="{CHECKED}">{DISPLAY_DATE}</time></p><p class="editorial-disclosure">Un comparatif rédigé par l’équipe Madeleine, à partir des sources officielles. <a href="/comparatifs/methode/">Lire notre méthode</a>.</p></header>
      <div class="comparison-layout">
        <aside class="comparison-toc"><nav aria-label="Sommaire du comparatif"><p class="toc-title">Dans ce comparatif</p><a href="#reponse">La réponse rapide</a><a href="#tableau">Le tableau comparatif</a><a href="#choisir">Lequel choisir ?</a><a href="#cas-pratique">À essayer chez vous</a><a href="#questions">Vos questions</a><a href="#sources">Les sources</a></nav></aside>
        <div class="comparison-body">
          <section id="reponse" class="quick-answer" aria-labelledby="reponse-title"><p class="eyebrow">La réponse rapide</p><h2 id="reponse-title">Deux approches à départager.</h2><p>{esc(item['summary'])}</p></section>
          <section id="tableau" aria-labelledby="tableau-title"><h2 id="tableau-title">Madeleine de Goût et {name}, point par point</h2><p>Comparez les tâches que vous voulez simplifier. Les références entre crochets renvoient aux sources sous le tableau.</p><p class="table-hint" id="table-hint">Sur petit écran, faites défiler le tableau horizontalement.</p><div class="comparison-table-wrap" tabindex="0" role="region" aria-label="Tableau comparatif de Madeleine de Goût et {name}" aria-describedby="table-hint"><table class="comparison-table"><caption>Comparaison des usages — informations vérifiées le {DISPLAY_DATE}</caption><thead><tr><th scope="col">Votre besoin</th><th scope="col">Madeleine de Goût<span class="table-subtitle">L’organisation du foyer · bêta</span></th><th scope="col">{name}<span class="table-subtitle">{esc(item['label'])}</span></th></tr></thead><tbody>{rows}</tbody></table></div><p class="table-footnote">« Non précisé » signifie que les pages consultées ne permettent pas de conclure. Cela ne signifie pas que la fonction est absente. Madeleine est encore en bêta.</p></section>
          <section id="choisir" aria-labelledby="choisir-title"><h2 id="choisir-title">Lequel choisir pour votre semaine ?</h2><p>Notre lecture des usages présentés ci-dessus :</p><div class="choice-grid"><div class="choice-card choice-madeleine"><p class="eyebrow">Essayez Madeleine si…</p><h3>Le point de départ, c’est votre foyer.</h3><p>{esc(item['madeleine_for'])}</p><a href="/telecharger.html">Découvrir la bêta</a></div><div class="choice-card"><p class="eyebrow">Regardez {name} si…</p><h3>{esc(item['strength'])}</h3><p>{esc(item['best_for'])}</p><a href="{esc(item['sources'][0][1])}" rel="noopener noreferrer">Consulter le site officiel</a></div></div><div class="watch-note"><h3>Le point à vérifier avant de décider</h3><p>{esc(item['watch'])}</p></div></section>
          <section id="cas-pratique" class="practical-case" aria-labelledby="cas-title"><p class="eyebrow">Un essai utile</p><h2 id="cas-title">{esc(item['scenario_title'])}</h2><p>{esc(item['scenario'])}</p><a href="/guides/organiser-repas-famille-gouts-differents/">Notre méthode pour préparer une semaine en famille</a></section>
          <section id="questions" class="comparison-faq" aria-labelledby="questions-title"><h2 id="questions-title">Vos questions sur Madeleine et {name}</h2>{faq}</section>
          <section id="sources" class="comparison-sources" aria-labelledby="sources-title"><h2 id="sources-title">Sources et date de vérification</h2><p>Sources officielles consultées le <time datetime="{CHECKED}">{DISPLAY_DATE}</time>. Les prix, versions et fonctions peuvent évoluer. Cette page est une analyse documentaire, sans test comparatif en conditions réelles.</p><ol>{sources}</ol><p>Pour Madeleine : <a href="/">présentation de l’application et captures de la bêta</a> et <a href="/telecharger.html">conditions d’accès actuelles</a>. <a href="mailto:paul@madeleine-de-gout.com">Signaler une correction</a>.</p></section>
        </div>
      </div>
    </article>
    <section class="related-comparisons" aria-labelledby="related-title"><p class="eyebrow">Continuez à comparer</p><h2 id="related-title">D’autres façons de préparer la semaine.</h2><div class="comparison-grid">{''.join(comparison_card(other) for other in related[:3])}</div><a class="quiet-link" href="/comparatifs/">Voir les 13 comparatifs</a></section>
    <section class="closing-cta"><img src="/images/mascotte.webp" alt="" width="160" height="160" loading="lazy"><div><p class="eyebrow">Et si vous essayiez ?</p><h2>Votre semaine. Vos goûts. Votre Madeleine.</h2><p>La bêta est disponible sur Android et sur iPhone via TestFlight.</p><a class="button" href="/telecharger.html">Essayer Madeleine</a></div></section>
    </main>'''
    faq_schema = {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in item['faq']]}
    destination = ROOT / path.strip('/') / 'index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    headline = f'Madeleine de Goût vs {item["name"]}.'
    destination.write_text(document(title, item['description'], path, body, [article_schema(headline, item['description'], path, item['sources']), crumbs_schema, faq_schema], article=True))


def build_hub(items: list[dict]) -> None:
    path = '/comparatifs/'
    title = 'Applications de menus et box repas : 13 comparatifs — Madeleine'
    description = 'Comparez Madeleine de Goût à Jow, HelloFresh, Quitoque, Samsung Food et 9 autres services : tableaux détaillés, usages, limites et sources officielles.'
    crumbs, crumbs_schema = breadcrumb([('Accueil', '/'), ('Comparatifs', path)])
    filters = ''.join(f'<button type="button" data-category-filter="{key}" aria-pressed="false">{esc(label)}</button>' for key, label in CATEGORIES.items())
    cards = ''.join(comparison_card(item, True) for item in items)
    table_rows = ''.join(f'<tr><th scope="row"><a href="/comparatifs/madeleine-vs-{item["slug"]}/">{esc(item["name"])}</a></th><td>{esc(item["label"])}</td><td>{esc(item["strength"])}</td><td><a href="/comparatifs/madeleine-vs-{item["slug"]}/#tableau">Voir les différences</a></td></tr>' for item in items)
    body = f'''<main id="contenu" class="comparison-page comparison-hub">{crumbs}
      <header class="comparison-hero"><p class="eyebrow">Bien choisir, mieux s’organiser</p><h1>À chaque cuisine,<br><span>son bon compagnon.</span></h1><p class="lead">Une application qui propose les menus, une liste partagée ou une box livrée ? Comparez ce que chaque service fait pour vous, puis choisissez ce qui simplifie vraiment votre semaine.</p><p class="article-meta">13 comparatifs · Sources officielles vérifiées le <time datetime="{CHECKED}">{DISPLAY_DATE}</time></p></header>
      <section class="comparison-intro-grid" aria-label="Comprendre les différences entre services"><div><p class="eyebrow">D’abord, votre besoin</p><h2>Vous voulez déléguer quoi ?</h2><p>Le choix des plats, l’organisation des courses et la livraison des ingrédients sont trois tâches différentes. Une box et une application peuvent se compléter.</p><a href="#vue-ensemble">Voir le tableau d’ensemble</a></div><div class="hub-editorial-note"><p class="eyebrow">Notre parti pris : la clarté</p><p>Ces comparatifs sont rédigés par l’équipe Madeleine. Nous indiquons aussi les usages où un autre service peut mieux vous convenir.</p><a href="/comparatifs/methode/">Notre méthode et ses limites</a></div></section>
      <section id="comparaisons" class="comparison-library" aria-labelledby="library-title"><div class="section-heading"><p class="eyebrow">Les comparatifs détaillés</p><h2 id="library-title">Trouvez votre point de comparaison.</h2></div><div class="comparison-tools" data-comparison-tools hidden><label for="comparison-search">Rechercher un service</label><input id="comparison-search" type="search" placeholder="Jow, HelloFresh, Paprika…" autocomplete="off"><div class="category-filters" role="group" aria-label="Filtrer par type de service"><button type="button" data-category-filter="all" aria-pressed="true">Tous les services</button>{filters}</div></div><p class="result-count" id="comparison-count" role="status" aria-live="polite">13 comparatifs disponibles.</p><div class="comparison-grid">{cards}</div><p class="empty-search" id="comparison-empty" hidden>Aucun service ne correspond. Essayez un autre nom ou choisissez « Tous les services ».</p></section>
      <section id="vue-ensemble" class="overview-section" aria-labelledby="overview-title"><p class="eyebrow">Le tableau d’ensemble</p><h2 id="overview-title">Des services différents, un même dîner à préparer.</h2><p>Chaque nom mène à un tableau détaillé et à ses sources. Cette vue décrit le positionnement, sans attribuer de note globale.</p><p class="table-hint" id="overview-hint">Sur petit écran, faites défiler le tableau horizontalement.</p><div class="comparison-table-wrap" role="region" tabindex="0" aria-label="Tableau d’ensemble des 13 services" aria-describedby="overview-hint"><table class="comparison-table overview-table"><caption>13 services, leurs usages et leur comparaison avec Madeleine</caption><thead><tr><th scope="col">Service</th><th scope="col">Type</th><th scope="col">À regarder pour…</th><th scope="col">Face à Madeleine</th></tr></thead><tbody>{table_rows}</tbody></table></div></section>
      <section class="comparison-method-preview"><div><p class="eyebrow">Ce que les tableaux ne disent pas seuls</p><h2>Une fonction cochée ne fait pas toute une semaine.</h2></div><div><p>Essayez un cas réel : un soir pressé, une personne absente et des légumes à utiliser. Comparez le nombre de décisions nécessaires pour arriver à votre menu et à vos courses.</p><p>Les mentions non documentées restent ouvertes. Les offres gratuites, les abonnements et les paniers alimentaires sont distingués.</p><a href="/comparatifs/methode/">Lire la méthode complète</a></div></section>
      <section class="closing-cta"><img src="/images/mascotte.webp" alt="" width="160" height="160" loading="lazy"><div><p class="eyebrow">Faites-vous votre propre idée</p><h2>Commencez par votre prochaine semaine.</h2><p>Découvrez la bêta Madeleine sur Android et iPhone.</p><a class="button" href="/telecharger.html">Essayer Madeleine</a></div></section>
    </main>'''
    collection = {'@type': 'CollectionPage', '@id': ORIGIN + path, 'name': title, 'description': description, 'url': ORIGIN + path, 'inLanguage': 'fr-FR', 'dateModified': CHECKED, 'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(items), 'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': f'Madeleine de Goût vs {item["name"]}', 'url': ORIGIN + f'/comparatifs/madeleine-vs-{item["slug"]}/'} for i, item in enumerate(items, 1)]}}
    (ROOT / 'comparatifs/index.html').write_text(document(title, description, path, body, [collection, crumbs_schema], script='comparisons.js'))


def build_method() -> None:
    path = '/comparatifs/methode/'
    title = 'Comment nous comparons les applications et box repas — Madeleine'
    description = 'Sources officielles, critères communs, dates, limites et transparence : découvrez la méthode des comparatifs publiés par Madeleine de Goût.'
    crumbs, crumbs_schema = breadcrumb([('Accueil', '/'), ('Comparatifs', '/comparatifs/'), ('Notre méthode', path)])
    body = f'''<main id="contenu" class="comparison-page method-page">{crumbs}<article><header class="comparison-hero"><p class="eyebrow">Notre méthode</p><h1>Comparer avec soin.<br><span>Vous laisser choisir.</span></h1><p class="lead">Nous développons Madeleine de Goût. Nous sommes donc partie prenante de ces comparatifs. Voici comment les lire et ce qu’ils permettent de conclure.</p><p class="article-meta">Par Madeleine de Goût · <time datetime="{CHECKED}">{DISPLAY_DATE}</time></p></header><div class="method-content">
      <section><h2>Des comparaisons documentaires, pas des tests de terrain</h2><p>Les pages s’appuient sur les sites, aides et présentations officiels des services consultés le {DISPLAY_DATE}. Nous n’avons pas passé une commande ni réalisé un essai complet de chaque application. Les cas pratiques sont des pistes d’essai pour vous, pas des résultats mesurés par notre équipe.</p></section>
      <section><h2>Des critères liés à votre quotidien</h2><p>Nous comparons le point de départ du menu, la planification, les courses, les réserves de la cuisine, les préférences du foyer et les conditions d’accès. Le format varie lorsque cela aide à comprendre un service : une box livre des aliments, un carnet conserve des recettes, une liste partagée coordonne les achats.</p><p>Les colonnes Madeleine décrivent le périmètre de la bêta et sa présentation sur ce site. Une bêta peut évoluer et comporter des limites. Les captures publiées sont issues de l’application.</p></section>
      <section><h2>Une information manquante reste une information manquante</h2><p>« Non précisé dans les sources » ne signifie jamais « indisponible ». Une page officielle peut omettre une fonction. Nous ne remplaçons pas cette incertitude par une croix rouge ou un score défavorable.</p><p>Chaque tableau renvoie aux sources consultées. Si une fonction dépend d’un abonnement ou d’un appareil, nous le précisons lorsque les sources le permettent.</p></section>
      <section><h2>Des prix qui doivent rester comparables</h2><p>Nous ne désignons pas l’application la moins chère et ne mélangeons pas le prix d’un abonnement avec celui d’une box contenant des aliments. Un calcul utile devrait porter sur le même nombre de repas et de personnes, inclure la livraison et distinguer les promotions du prix habituel.</p><p>Les conditions de la bêta Madeleine sont à vérifier lors de l’accès. Nous n’inventons pas de tarif public pour remplir une case du tableau.</p></section>
      <section><h2>Des conclusions que vous pouvez examiner</h2><p>Les paragraphes « Lequel choisir ? » sont notre interprétation des usages documentés. Nous expliquons aussi dans quels cas le service comparé peut vous convenir. Aucun classement par étoiles, témoignage client ou pourcentage d’économies n’a été créé pour ces pages.</p><p>Les noms cités appartiennent à leurs titulaires. Leur présence ne suggère ni partenariat ni approbation de Madeleine. Les liens de sources servent à vérifier l’information ; aucun code promotionnel ou lien d’affiliation n’est ajouté dans ces comparatifs.</p></section>
      <section><h2>Une date qui correspond à une vérification</h2><p>La date visible est celle de la vérification éditoriale des sources, pas une date renouvelée automatiquement. Mealime fait l’objet d’un traitement distinct puisque son éditeur annonce son arrêt au 21 octobre 2026.</p><p>Pour signaler une erreur ou une évolution, écrivez à <a href="mailto:paul@madeleine-de-gout.com">paul@madeleine-de-gout.com</a> avec la page concernée et une source officielle.</p></section>
      <p><a class="button" href="/comparatifs/">Parcourir les 13 comparatifs</a></p>
    </div></article></main>'''
    destination = ROOT / 'comparatifs/methode/index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document(title, description, path, body, [article_schema('Comparer avec soin. Vous laisser choisir.', description, path, []), crumbs_schema], article=True))


def build() -> None:
    items = json.loads((ROOT / 'scripts/comparisons.json').read_text())
    if len({item['slug'] for item in items}) != len(items):
        raise ValueError('Les slugs doivent être uniques')
    for item in items:
        build_detail(item, items)
    build_hub(items)
    build_method()
    print(f'{len(items)} comparatifs, une rubrique et une méthode générés.')


if __name__ == '__main__':
    build()
