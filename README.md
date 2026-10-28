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
- `js/animation.js` : thème mémorisé, menu mobile, immersion réversible au défilement, barre macOS et Dock, filtres, fiches projets, copie de l’e-mail. Les détails des fiches sont regroupés dans l’objet `projects`.
- `assets/` : variantes WebP optimisées, image de partage JPEG, favicon et CV PDF fourni sous forme d’image dans un PDF téléchargeable. Le CV n’est pas chargé avant son téléchargement.

Les six projets présentés sont PANDRONE au LaBRI, Pollen Robotics, StackEasy, Argus, Archéovision et Hexacup. Les informations proviennent du CV et du texte LinkedIn transmis par Anatole. La date StackEasy reste **2025**, confirmée par Anatole malgré une date différente dans l’en-tête LinkedIn. Le parcours comprend aussi la formation Mainframe de 399 heures chez ESTIAC AGILE CONCEPT. PANDRONE est présenté comme un travail en cours depuis octobre 2026, sans résultat chiffré inventé.

Les visuels de projets sont des illustrations SVG/CSS, signalées comme telles ; les projets confidentiels n’ont pas de lien de dépôt inventé. Le PDF téléchargeable reste le CV original fourni.

L’écran du bureau utilise les mêmes couleurs que le thème du site, y compris son bandeau supérieur. Un petit Dock illustratif préfigure les applications. En entrant dans l’écran au défilement, la navigation devient une barre inspirée de macOS et un Dock fonctionnel apparaît : projets, parcours, GitHub, LinkedIn, e-mail, CV et retour au bureau. Le Dock persiste dans les sections suivantes et disparaît en remontant vers l’accueil. GitHub et LinkedIn s’ouvrent dans un nouvel onglet ; le profil utilisé est https://www.linkedin.com/in/anatole-garnier1/.

La barre affiche la date et l’heure locales du navigateur. L’horloge ne tourne que lorsque le mode bureau est actif et la page visible. Le changement de navigation réserve une hauteur constante pour préserver la position de défilement. Les liens directs vers les sections activent également le Dock, et le mode de réduction des animations donne accès aux raccourcis sans zoom. Le Dock masqué est `inert` et retiré de l’arbre d’accessibilité.

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

Les contrôles couvrent les thèmes et l’écran synchronisé, huit largeurs de 320 à 1 920 px en navigation classique et macOS, l’immersion réversible, le Dock et ses liens, le retour au bureau, les accès directs, les filtres, les six fiches projets, le clavier, le menu, le CV, la copie de l’e-mail, les anciennes URL, la navigation sans JavaScript et la réduction des animations. Les captures et le rapport sont enregistrés dans `.artifacts/`, ignoré par Git. Un fichier axe-core local `.artifacts/axe.min.js` active aussi les contrôles automatiques WCAG A/AA ; ces contrôles ont été exécutés pendant la réalisation. Ils ne remplacent pas un audit manuel complet.
