# Madeleine de Goût — site public

Site statique publié par GitHub Pages : https://madeleine-de-gout.com.
La page à partager dans WhatsApp ou un message est toujours
https://madeleine-de-gout.com/telecharger.html.

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
- Aucun JavaScript sur l'accueil et la politique de confidentialité. La page de
  téléchargement utilise uniquement `download.js`, sans code intégré au HTML,
  `eval`, insertion HTML ou destination calculée depuis les paramètres de l'URL.
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
python3 -m http.server 8000 --bind 127.0.0.1
```

Pour tester les ressources dans un navigateur local, utiliser un serveur HTTPS
local : `upgrade-insecure-requests` peut faire passer les ressources HTTP locales
en HTTPS. Ne jamais désactiver cette protection dans la version publiée pour
contourner un problème de prévisualisation. Vérifier mobile et ordinateur, avec et
sans JavaScript, ainsi que l'accès au fichier APK et les liens TestFlight.

Ce dépôt est **public**. Ne jamais y placer de clé Apple, clé privée, `.env`,
identifiant de démonstration, mot de passe, capture de compte ou export de données.
La branche de travail pour cette évolution est `codex/site-testflight-security`.
