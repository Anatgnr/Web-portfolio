# Portfolio — Anatole Garnier

Portfolio en français, statique et responsive, inspiré des interfaces Apple. HTML sémantique, CSS natif et JavaScript sans dépendance côté visiteur. Aucun service tiers, police distante ou traceur.

## Aperçu local

Depuis la racine du dépôt :

```sh
python -m http.server 8000
```

Ouvrir http://localhost:8000. Aucun `npm install` ni compilation nécessaire. Python sert uniquement à l’aperçu et au packaging ; le site fonctionne sur un hébergement statique.

## GitHub Pages

Dans **Settings → Pages → Build and deployment → Source**, sélectionner **GitHub Actions**. Le workflow `.github/workflows/pages.yml` publie le contenu de `_site` après chaque push sur `main`, ou via **Actions → Deploy portfolio to GitHub Pages → Run workflow**. Le dossier publié contient seulement les fichiers publics.

URL prévue : https://anatgnr.github.io/Web-portfolio/

Le site utilise des chemins relatifs compatibles avec le sous-dossier GitHub Pages. Les anciennes pages redirigent vers leurs sections respectives. Pour un autre nom de dépôt ou un domaine personnalisé, mettre à jour les URL absolues de `index.html`, `sitemap.xml`, `robots.txt`, des trois pages dans `html/`, ainsi que le lien de retour dans `404.html`.

## Contenu et interactions

- `index.html` : textes, projets, parcours, compétences, portrait, coordonnées, métadonnées et données structurées `ProfilePage` / `Person`.
- `css/stylesheet.css` : mise en page, responsive, thèmes, impression et mode de réduction des animations.
- `js/animation.js` : thème mémorisé, menu mobile, immersion réversible au défilement, filtres, fiches projets, copie de l’e-mail. Les détails des fiches sont regroupés dans l’objet `projects`.
- `assets/` : variantes WebP optimisées, image de partage JPEG, favicon et CV PDF fourni sous forme d’image dans un PDF téléchargeable. Le CV n’est pas chargé avant son téléchargement.

Les visuels de projets sont des illustrations SVG/CSS, signalées comme telles. Les informations et les résultats présentés proviennent du CV fourni ; les projets confidentiels n’ont pas de lien de dépôt inventé.

Le thème suit le système jusqu’à un choix explicite, enregistré localement. Le zoom respecte `prefers-reduced-motion` et comporte un lien pour accéder directement aux projets. Le contenu principal reste accessible sans JavaScript ; filtres, menu compact et fiches détaillées nécessitent JavaScript.

## Référencement et performance

Le contenu principal est livré directement en HTML : titre, description, URL canonique, Open Graph, Twitter Card, données structurées, sitemap et liens explorables. Après publication, ajouter l’URL à Google Search Console et y soumettre `sitemap.xml`. Sur un site de projet GitHub Pages, seul le fichier `/robots.txt` à la racine de `anatgnr.github.io` est pris en compte par les robots ; le fichier de ce dépôt devient utile si le site est servi à la racine d’un domaine personnalisé. Le sitemap peut être soumis directement à Search Console dans tous les cas. Ces dispositions facilitent l’exploration, sans garantir le classement.

Documentation : [SEO JavaScript, Google Search Central](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) · [Déploiement GitHub Pages](https://docs.github.com/en/get-started/start-your-journey/deploying-your-website-automatically).

Les images du bureau sont préchargées avec des variantes responsives ; le portrait est chargé à la demande. Les animations de zoom utilisent `transform` et `opacity`, avec un calcul limité à une fois par frame lorsque la scène est visible.

## Packaging manuel

```sh
python scripts/build.py
python -m http.server 8000 --directory _site
```

Les originaux fournis et les anciens médias dans `img/` sont conservés ; ils ne sont pas inclus dans la publication.

## Vérifications dans un navigateur

```sh
python -m pip install -r requirements-dev.txt
python scripts/build.py
python scripts/check_site.py
```

Ces dépendances sont réservées aux tests et ne sont pas publiées. Le script utilise Chrome déjà installé sous Windows ; pour un autre système, définir `CHROME_PATH` avec le chemin de Chrome ou Chromium. Il lance et arrête son propre serveur, monté sur `/Web-portfolio/`, pour vérifier les chemins réels d’hébergement.

Les contrôles couvrent les thèmes, huit largeurs de 320 à 1 920 px, l’immersion réversible, les filtres, les fiches projets, le clavier, le menu, le CV, la copie de l’e-mail, les anciennes URL, la navigation sans JavaScript et la réduction des animations. Les captures et le rapport sont enregistrés dans `.artifacts/`, ignoré par Git. Un fichier axe-core local `.artifacts/axe.min.js` active aussi les contrôles automatiques WCAG A/AA ; ces contrôles ont été exécutés pendant la réalisation. Ils ne remplacent pas un audit manuel complet.
