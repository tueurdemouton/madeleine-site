# SEO et organisation éditoriale — 18 novembre 2026

## Parcours du site

- `/` : comprendre l’application et rejoindre la bêta.
- `/guides/` : trouver les contenus disponibles ; chaque carte mène à un guide réel.
- `/guides/<sujet>/` : répondre à une question précise, avec un exemple utilisable et un lien vers l’application.
- `/telecharger.html` : installer la bêta Android ou rejoindre TestFlight sur iPhone.
- `/confidentialite.html` : consulter la politique de confidentialité existante.

La navigation garde deux entrées, « L’application » et « Guides & menus »,
avec un bouton distinct « Essayer la bêta ». Sur mobile, les deux entrées restent
visibles sur une seconde ligne. Les guides utilisent un fil d’Ariane, un sommaire
et une largeur de lecture limitée. Aucun menu masqué, filtre vide ou lien vers un
article à venir n’est nécessaire pour démarrer.

## Deux nouvelles pages par semaine

Les sujets sont des propositions éditoriales, sans mesure de volume de recherche.
Avant rédaction, comparer les pages existantes et les résultats de recherche pour
confirmer que le besoin traité est distinct. L’accueil conserve l’intention
« application de menus de la semaine en famille ».

| Semaine | Première page | Deuxième page |
| --- | --- | --- |
| 18–22 novembre 2026 | Organiser les repas d’une famille aux goûts différents (premier guide créé) | Menu de décembre : 7 dîners pour 4 et liste de courses |
| 23–29 novembre | Liste de courses pour la semaine : exemple pour 4 | Menu de Noël petit budget pour 6 |
| 30 novembre–6 décembre | Batch cooking d’hiver : préparer 5 dîners familiaux | Préparer les repas de Noël à l’avance |
| 7–13 décembre | Repas du soir en famille en 20 minutes | Que faire avec les restes des repas de fêtes ? |
| 14–20 décembre | Budget courses d’une famille de 4 : méthode et exemple | Menu de janvier économique : 7 dîners pour 4 |
| 21–27 décembre | Menu végétarien d’hiver pour une semaine | Que faire avec un reste de raclette ? |
| 28 décembre–3 janvier 2027 | Que cuisiner avec ce qui reste dans le frigo ? | Organiser les repas d’une famille aux horaires différents |

## Préparer le prochain guide

1. Choisir une URL durable sous `guides/`, avec un dossier contenant `index.html`.
2. Reprendre les ressources locales, la navigation et le pied de page d’un guide existant.
3. Rédiger un titre et une description propres à la page. Renseigner l’URL canonique,
   Open Graph, la date et l’auteur réels ; conserver un seul `h1`.
4. Donner une réponse complète avant de présenter l’application. Proposer un menu,
   une liste, un exemple ou un planning adapté au sujet. Identifier clairement les
   exemples fictifs et les préparations indicatives ; ne pas annoncer de test non effectué.
5. Pour une page de menus : détailler les recettes, les portions, les quantités et
   les ingrédients du placard. Pour un budget : dater et sourcer les prix, en
   distinguant coût des portions et montant du panier. Mesurer les temps annoncés.
6. Ajouter la carte du nouveau contenu à `/guides/` et des liens depuis les pages
   complémentaires. Ne pas créer de page presque identique pour une variante de mot-clé.
7. Les guides fonctionnent sans JavaScript. Le planning est un PDF A4 d'une page,
   généré depuis les sept jours du HTML par `python3 scripts/build_planning_pdf.py`
   sur macOS (Swift/Xcode). Le régénérer si la semaine d'exemple change.
8. Lancer `python3 scripts/build_sitemap.py`, puis `python3 scripts/check_site.py`.
9. Vérifier mobile, clavier, liens, images et impression avant publication.

Le premier guide propose une méthode d’organisation et des plats indicatifs ;
il ne remplace pas la future page de menu avec recettes et quantités complètes.

## Search Console et suivi

Valider la propriété du domaine dans le compte Google du propriétaire, puis
transmettre `https://madeleine-de-gout.com/sitemap.xml`. Inspecter l’accueil,
la rubrique et le premier guide après publication. Ni le sitemap ni une demande
d’exploration ne garantissent l’indexation ou un classement.

Chaque mois, relever les pages indexées, les requêtes hors marque, les impressions
et les clics. Suivre séparément les essais de la bêta quand une mesure adaptée sera
en place ; aucun outil de mesure tiers n’est ajouté par cette version.

## Références

- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
