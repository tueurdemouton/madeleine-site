# Madeleine de Goût — site public

Site statique publié par GitHub Pages : https://madeleine-de-gout.com.
La page à partager dans WhatsApp ou un message est toujours
https://madeleine-de-gout.com/telecharger.html.

## Référencement

Le site autorise son indexation par les moteurs de recherche (choix du 2026-11-15,
complété le 2026-11-18 par les premiers guides SEO). Aucune page ne
déclare `noindex`, `nofollow` ni `noimageindex`, et le contrôle automatique
vérifie leur absence. Les aperçus de partage WhatsApp restent déclarés par les
balises Open Graph.

Le logo affiché par Google est l'icône déclarée par `<link rel="icon">` sur la
page d'accueil : `favicon.ico` (16, 32, 48) et `images/icon-192.png`, la
mascotte de l'app. Google la met à jour à son rythme, après avoir exploré de
nouveau la page d'accueil ; une demande d'exploration dans Search Console ne
garantit pas sa date de mise à jour.

Référence : https://developers.google.com/search/docs/appearance/favicon-in-search

Le site possède une rubrique `/guides/` et des articles sous `/guides/<sujet>/`.
Le parcours, le calendrier éditorial et la procédure d'ajout d'une page sont
documentés dans [docs/seo-editorial.md](docs/seo-editorial.md).
Les URL publiques sont déclarées dans `sitemap.xml`, lui-même indiqué dans
`robots.txt`. Régénérer le sitemap après un ajout de page :

```sh
python3 scripts/build_sitemap.py
python3 scripts/check_site.py
```

Le contrôle parcourt aussi les sous-dossiers, vérifie les URL canoniques, les
ancres entre pages et la cohérence du sitemap. Le guide utilise les microdonnées
Article et BreadcrumbList, sans script intégré au HTML ni dépendance tierce.
Les guides et leur sommaire fonctionnent sans JavaScript. Le planning est fourni
en PDF A4 d'une page, téléchargeable et imprimable. Après une modification des
sept jours de l'exemple, le régénérer sur macOS avec
`python3 scripts/build_planning_pdf.py` (Swift/Xcode requis uniquement pour
la génération, aucune dépendance à charger chez les visiteurs).

## Installation de la bêta

- Android : le fichier `madeleine-de-gout.apk` présent dans ce dépôt.
- iPhone : installer TestFlight, puis rejoindre le groupe public
  https://testflight.apple.com/join/WRTVBuNv.
- La page met en premier le parcours correspondant au téléphone, sans redirection
  automatique et sans envoyer cette détection à un serveur. Les deux choix restent
  accessibles, y compris si JavaScript est désactivé.
- La copie du lien utilise le presse-papiers uniquement après un clic. Si le
  navigateur le refuse, le champ est sélectionné pour permettre la copie manuelle.

Le 7 novembre 2026, le build iOS 1.0.2 (3) est `WAITING_FOR_BETA_REVIEW`.
Quand Apple l'approuve, retirer le paragraphe `.availability-note` de
`telecharger.html`. Ce statut n'est pas interrogé depuis le navigateur : aucune
clé App Store Connect ne doit figurer dans ce dépôt public. Mettre les étapes
à jour si les exigences de l'app ou les liens de distribution changent.

## Protections présentes dans le code

- CSP restrictive sur chaque page, placée avant toute ressource : aucune connexion
  réseau depuis le code des pages, aucun formulaire, plugin, base URL ou contenu
  embarqué ; ressources visuelles, styles et police servis localement.
- Aucun JavaScript sur la politique de confidentialité. L'accueil utilise
  `effects.js` ; le téléchargement utilise `download.js` et `effects.js`, sans
  code intégré au HTML, `eval`, insertion HTML ou destination calculée depuis
  les paramètres de l'URL.
- Aucun framework, paquet npm, outil de mesure ou script tiers chargé chez les
  visiteurs. Nunito est hébergée localement, avec sa licence OFL dans `fonts/`.
- Politique `no-referrer` sur toutes les pages. Les liens externes d'installation
  pointent explicitement vers l'App Store et TestFlight.
- Contrôle hors réseau des pages et de leurs liens : `python3 scripts/check_site.py`.
  Ce contrôle tourne aussi dans GitHub Actions, avec des permissions de lecture,
  sans conserver les identifiants Git et avec l'action checkout épinglée à un commit.

Ces mesures réduisent les possibilités d'injection dans le navigateur. Elles ne
remplacent pas la sécurité des comptes GitHub/OVH ni les protections de l'hébergeur
contre les attaques de disponibilité.

## Réglages d'hébergement à terminer

Le contrôle du 7 novembre 2026 a observé un HTTP 200 sur
`http://madeleine-de-gout.com/telecharger.html`, sans redirection vers HTTPS.
Le certificat HTTPS existe, mais l'option **Enforce HTTPS** reste à activer dans :
https://github.com/tueurdemouton/madeleine-site/settings/pages.
L'accès Git par SSH fonctionne ; aucun accès API GitHub n'était configuré dans
cette session pour modifier ce réglage. Vérifier ensuite que HTTP renvoie vers HTTPS.
La directive CSP `upgrade-insecure-requests` protège les chargements de ressources,
mais ne remplace pas cette redirection du premier accès au site.

Les en-têtes HTTP personnalisés ne se configurent pas dans ce dépôt avec GitHub
Pages. Ne pas ajouter de `_headers`, `.htaccess` ou de balise `X-Frame-Options` en
prétendant qu'ils activent une protection. La protection contre l'intégration du
site dans une iframe (`frame-ancestors`) exige un véritable en-tête HTTP ; elle
ne fonctionne pas dans une CSP en balise meta. Pour l'ajouter, il faudra une couche
HTTP qui permet ces en-têtes, en conservant la disponibilité des téléchargements.
Aucun changement d'hébergeur ou de DNS n'a été effectué.

Vérifier également le domaine personnalisé dans les réglages Pages du compte
GitHub, ce qui réduit le risque d'appropriation par un autre compte GitHub. Le TXT
`_github-pages-challenge-tueurdemouton.madeleine-de-gout.com` n'était pas présent
lors du contrôle ; cela ne suffit pas à déterminer tous les états de vérification
possibles du compte. Les A du domaine et le CNAME de `www` pointaient correctement
vers GitHub Pages, sans résolution du sous-domaine inutilisé testé.

Références :
- HTTPS : https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https
- Domaine : https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages/verifying-your-custom-domain-for-github-pages
- Limites de `frame-ancestors` : https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors

## Vérifier et prévisualiser

```sh
python3 scripts/check_site.py
```

Pour tester les ressources dans un navigateur local, utiliser un serveur HTTPS
local : `upgrade-insecure-requests` peut faire passer les ressources HTTP locales
en HTTPS. Ne jamais désactiver cette protection dans la version publiée pour
contourner un problème de prévisualisation. Vérifier mobile et ordinateur, avec et
sans JavaScript, ainsi que l'accès au fichier APK et les liens TestFlight.

Ce dépôt est **public**. Ne jamais y placer de clé Apple, clé privée, `.env`,
identifiant de démonstration, mot de passe, capture de compte ou export de données.
La branche de travail pour cette évolution est `codex/site-testflight-security`.

## Vérifications de cette version

L'accueil, la rubrique des guides et le premier article utilisent des captures
réelles de la bêta en français (15 novembre 2026). Elles illustrent la semaine,
le remplacement d'un plat et la liste de courses. Les WebP en 360 et 720 pixels
sont servis via `srcset`, avec dimensions réservées, chargement différé hors du
premier écran et liens d'agrandissement sans JavaScript. Leur provenance est
documentée dans `images/application/README.md`.

Le 18 novembre 2026, WebKit a vérifié l'accueil en 320 px, 375 px et 1440 px,
la rubrique Guides & menus en 375 px et 1440 px, et le premier guide en 320 px
sans JavaScript, 375 px et 1440 px. Aucun débordement horizontal ; images et police
chargées, navigation au clavier et liens de sommaire accessibles. Les liens de
navigation et le bouton principal mesurent au moins 44 px de haut.
Le téléchargement et la confidentialité ont aussi été contrôlés sur mobile.
Le PDF téléchargeable est un document A4 d'une page : les sept jours et leur titre
ont été vérifiés dans le texte du PDF, puis son rendu a été inspecté.

WebKit a vérifié l'accueil en 375 px et 1440 px, et la page de téléchargement en
360 px (Android), 390 px (iPhone), 1280 px (ordinateur) et 375 px sans JavaScript.
Aucun débordement horizontal, les images et la police sont chargées, les deux
parcours restent disponibles et le lien copié est fixe. Le parcours détecté est
placé en premier dans le DOM, ce qui garde le même ordre au clavier.

Les tentatives locales de script intégré, de script externe, de connexion réseau
et d'envoi de formulaire ont été bloquées par la CSP dans WebKit. Des paramètres
URL contenant une destination externe ou du HTML n'ont pas modifié les liens.
Le fichier APK, les images et le domaine CNAME n'ont pas été modifiés.

La version du lien CSS évite de conserver les anciens styles dans le cache après
cette publication. Faire évoluer ce paramètre lors d'une prochaine modification
visuelle nécessitant un nouveau chargement immédiat des styles.

## Animations

Les effets sont locaux, sans bibliothèque ni ressource externe. Les décorations
CSS du premier écran durent au maximum 4,8 secondes, puis s'arrêtent. Les cartes
apparaissent une seule fois au défilement avec IntersectionObserver et Web
Animations ; les boutons d'installation restent disponibles immédiatement.

La préférence `prefers-reduced-motion` désactive les animations CSS et JavaScript,
y compris lorsqu'elle change pendant la consultation. Un déplacement du focus
clavier vers une zone animée termine son animation. Sans JavaScript ou sans les
API d'animation, les contenus restent affichés normalement. Les petits effets
à l'ouverture des aides sont déclenchés uniquement par l'utilisateur.

## Logos des plateformes

Les pictogrammes Android et Apple sont issus de Font Awesome Free 7.3.1,
par Fonticons, sous licence CC BY 4.0. Les tracés sont conservés ; seule leur
couleur est fixée dans le SVG pour un affichage identique dans les navigateurs.
Les fichiers sont servis localement, sans bibliothèque ni chargement externe.
La licence est conservée dans `images/PLATFORM-ICONS-LICENSE.txt` et les mentions
d'attribution d'origine sont présentes dans les SVG.

Sources :
- https://github.com/FortAwesome/Font-Awesome/blob/7.3.1/svgs/brands/android.svg
- https://github.com/FortAwesome/Font-Awesome/blob/7.3.1/svgs/brands/apple.svg
