# Présidentielle 2027 — Simulateur V4

Simulateur statique. L’interface et le calcul sont dans `index.html` et `app.js`. Les données sont séparées dans `data/candidates.json`, `data/polls.json` et `data/scenarios.json`.

## Lancer en local

Le navigateur doit pouvoir charger les fichiers JSON par HTTP. Depuis la racine du projet :

```sh
ruby --disable-gems -run -e httpd . -p 8000 -b 127.0.0.1
```

Ouvrir ensuite <http://127.0.0.1:8000>. Le déploiement Netlify sert ces mêmes fichiers statiques.

## Données et règles

- `candidates.json` est le référentiel des personnalités et de leur statut (`declared`, `envisaged`, `withdrawn`, `ineligible` ou `official`).
- `polls.json` contient les instantanés par configuration de candidatures. Un score n’est utilisable qu’avec la liste `candidateIds` qui le définit.
- `scenarios.json` contient les hypothèses pédagogiques de reports et les personnalités proposées dans le sélecteur.
- `scripts/update_polls.py` récupère le flux public Mieux Voter et ne retient que les enquêtes du premier tour dont la liste est exactement identique à la configuration locale. Il calcule une moyenne pondérée par fraîcheur et taille d’échantillon. Si aucune correspondance n’existe, l’instantané local n’est pas remplacé.
- `scripts/validate_data.py` contrôle les identifiants, statuts, configurations, scores et reports de voix.

Les scénarios de partage restent dans le fragment `#s=` de l’URL. Les anciennes URL V3, sans `configurationId`, continuent de charger la configuration de référence.

## Mise à jour et déploiement

`.github/workflows/update-polls.yml` actualise les sondages chaque jour à 06:17 UTC et valide les données avant commit. Le commit sur `main` déclenche `.github/workflows/netlify.yml` après une nouvelle validation.

Configurer les secrets GitHub `NETLIFY_AUTH_TOKEN` et `NETLIFY_SITE_ID`. `netlify.toml` publie la racine du projet et fixe un cache court pour les fichiers de données. Une fois le dépôt relié et les secrets définis, les mises à jour passent automatiquement par GitHub Actions et Netlify.

Les intentions sont des mesures conditionnelles aux configurations testées, et ne sont pas des prévisions. Attribution des données : [Mieux Voter / presidentielle2027](https://github.com/MieuxVoter/presidentielle2027), licence MIT.
