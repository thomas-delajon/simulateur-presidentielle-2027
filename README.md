# Présidentielle 2027 — Simulateur V4

Simulateur statique. L’interface et le calcul sont dans `index.html` et `app.js`. Les données sont séparées dans `data/candidates.json`, `data/polls.json` et `data/scenarios.json`.

## Lancer en local

Le navigateur doit pouvoir charger les fichiers JSON par HTTP. Depuis la racine du projet :

```sh
npm run dev
```

Node.js 18 ou une version plus récente est nécessaire. Aucune dépendance n'est à installer. Ouvrir ensuite <http://127.0.0.1:8000>. Le déploiement Netlify sert ces mêmes fichiers statiques.

La commande construit le site dans `dist/`, génère `robots.txt` et `sitemap.xml`, puis injecte l'URL canonique. En local, cette URL est `http://127.0.0.1:8000`. Sur Netlify, l'adresse principale du site ou le domaine personnalisé est utilisé automatiquement.

## Données et règles

- `candidates.json` est le référentiel des personnalités et de leur statut (`declared`, `envisaged`, `withdrawn`, `ineligible` ou `official`).
- `polls.json` contient les instantanés par configuration de candidatures. Un score n’est utilisable qu’avec la liste `candidateIds` qui le définit.
- `scenarios.json` contient les hypothèses pédagogiques de reports et les personnalités proposées dans le sélecteur.
- `scripts/update_polls.py` récupère le flux public Mieux Voter et ne retient que les enquêtes du premier tour dont la liste est exactement identique à la configuration locale. Il calcule une moyenne pondérée par fraîcheur et taille d’échantillon. Si aucune correspondance n’existe, l’instantané local n’est pas remplacé.
- `scripts/validate_data.py` contrôle les identifiants, statuts, configurations, scores et reports de voix.

Les scénarios de partage restent dans le fragment `#s=` de l’URL. Les anciennes URL V3, sans `configurationId`, continuent de charger la configuration de référence.

## Mise à jour et déploiement

`.github/workflows/update-polls.yml` actualise les sondages chaque jour à 06:17 UTC et valide les données avant commit. Chaque commit sur `main` déclenche ensuite un déploiement automatique lorsque le dépôt GitHub est relié directement au projet Netlify.

`netlify.toml` valide les données, construit le site dans `dist/`, ajoute les en-têtes de sécurité et fixe un cache court pour les données. Aucun jeton Netlify ne doit être enregistré dans GitHub.

Les intentions sont des mesures conditionnelles aux configurations testées, et ne sont pas des prévisions. Attribution des données : [Mieux Voter / presidentielle2027](https://github.com/MieuxVoter/presidentielle2027), licence MIT.
