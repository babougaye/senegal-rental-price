# Senegal Rental Price

![CI](https://github.com/<org>/senegal-rental-price/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/<org>/senegal-rental-price/actions/workflows/cd.yml/badge.svg)

Service de prédiction du prix de location d'un bien immobilier au Sénégal
(Dakar, Thiès, Saint-Louis, Mbour, Saly), de l'entraînement du modèle jusqu'à
son exposition via une API REST, packagée et déployable avec Docker.

> Projet M2 DSIA — Babou Gaye & Mouhamed Diouf

## Sommaire

- [Installation](#installation)
- [Générer les données](#générer-les-données)
- [Entraîner un modèle](#entraîner-un-modèle)
- [Lancer l'API](#lancer-lapi)
- [Lancer le front](#lancer-le-front)
- [Lancer les tests](#lancer-les-tests)
- [Tout lancer avec Docker](#tout-lancer-avec-docker)
- [Structure du projet](#structure-du-projet)

## Installation

Prérequis : Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Générer les données

Le jeu de données est synthétique (voir `data/README.md` pour la méthodologie).

```bash
python -m senegal_rental_price.data.generate_synthetic_data \
    --n-rows 4000 --seed 42 --output data/raw/locations_senegal.csv
```

## Entraîner un modèle

L'entraînement est configuré avec [Hydra](https://hydra.cc) — aucun paramètre
n'est codé en dur. Le tracking des runs se fait avec MLflow.

```bash
# Modèle par défaut (random_forest)
python -m senegal_rental_price.models.train

# Changer de modèle et d'hyperparamètres en ligne de commande
python -m senegal_rental_price.models.train model=xgboost model.params.max_depth=8
python -m senegal_rental_price.models.train model=ridge

# Visualiser les runs (backend par défaut : sqlite local)
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

> ⚠️ **Deux backends MLflow distincts et indépendants coexistent dans ce
> projet :**
> - Par défaut (`conf/config.yaml`), l'entraînement écrit dans
>   `sqlite:///mlflow.db`, un fichier local à la racine du projet. C'est ce
>   backend qu'il faut consulter avec la commande `mlflow ui` ci-dessus.
> - Le service `mlflow` de `docker-compose.yml` (section
>   [Tout lancer avec Docker](#tout-lancer-avec-docker)) démarre un serveur
>   **séparé**, avec son propre stockage dans `mlflow_data/` (vide au premier
>   lancement). Il ne contient **pas** automatiquement les runs entraînés en
>   local. Pour l'utiliser, démarrez-le puis pointez l'entraînement dessus :
>   `python -m senegal_rental_price.models.train mlflow.tracking_uri=http://localhost:5000`.
>
> En cas de message "Aucune exécution enregistrée" dans l'UI MLflow,
> vérifiez que vous consultez bien le même backend que celui utilisé pour
> l'entraînement.

Le modèle entraîné et ses métadonnées (métriques, colonnes de features, date
d'entraînement) sont sauvegardés dans `models/<nom_modele>.joblib` et
`models/<nom_modele>.metadata.json`.

## Lancer l'API

```bash
export SRP_MODEL_NAME=random_forest   # modèle à charger au démarrage
uvicorn api.main:app --reload
```

Documentation interactive : http://localhost:8000/docs

Endpoints :

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | Vérification de l'état du service |
| GET | `/model/info` | Métadonnées du modèle chargé |
| POST | `/predict` | Prédiction du prix à partir des caractéristiques d'un bien |

## Lancer le front

```bash
export SRP_API_URL=http://localhost:8000
streamlit run frontend/streamlit_app.py
```

### Bonus : front React

Une alternative React (Vite + Tailwind) est disponible dans
`frontend/react-app/` — voir `frontend/react-app/README.md` pour les
détails. Démarrage rapide :

```bash
cd frontend/react-app
npm install
cp .env.example .env
npm run dev
```
→ http://localhost:5173 (nécessite l'API démarrée sur le port 8000).

## Lancer les tests

```bash
pytest --cov=src --cov-report=term-missing
```

Le seuil de couverture minimal est de 70 % sur `src/` (appliqué aussi en CI).

## Tout lancer avec Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

> Le nom de projet Compose est fixé explicitement à `senegal-rental-price`
> (champ `name:` dans docker-compose.yml), donc les conteneurs/réseaux créés
> sont préfixés `senegal-rental-price_` quel que soit le dossier depuis
> lequel la commande est lancée.

- API : http://localhost:8000/docs
- Front (Streamlit) : http://localhost:8501
- MLflow : http://localhost:5000

Pour lancer le front React en bonus à la place (ou en plus) du front
Streamlit :

```bash
docker compose -f docker/docker-compose.yml --profile react up --build
```
→ front React sur http://localhost:5174

> Le dossier `models/` doit contenir un modèle entraîné (`*.joblib` +
> `*.metadata.json`) avant de lancer l'API — entraînez-en un avec la commande
> ci-dessus si nécessaire.

## Intégration et déploiement continus (CI/CD)

- **CI** (`.github/workflows/ci.yml`) : à chaque push/PR sur `main` —
  `ruff check` → `black --check` → `mypy --strict` sur `src/` → `pytest`
  avec seuil de couverture 70 % → build de l'image Docker de l'API. Le job
  `docker-build` dépend du job `quality` (`needs: quality`) : aucune image
  n'est construite si le lint, le typage ou les tests échouent.

- **CD (bonus)** (`.github/workflows/cd.yml`) : à chaque push sur `main`
  (donc après un merge de PR), republie automatiquement les images `api` et
  `frontend` sur GitHub Container Registry, après réexécution complète du
  CI comme "reusable workflow" (`needs: quality`). Images publiées :
  `ghcr.io/<owner>/<repo>/api:latest` et `ghcr.io/<owner>/<repo>/frontend:latest`
  (+ tag par SHA de commit). Aucun secret à configurer : le `GITHUB_TOKEN`
  fourni automatiquement par GitHub Actions suffit.

## Structure du projet

```
senegal-rental-price/
├── conf/              # Configuration Hydra (modèle, données)
├── data/              # raw/ (non versionné), processed/, README provenance
├── notebooks/         # Exploration — jamais de logique de prod
├── src/senegal_rental_price/
│   ├── data/           # Génération + nettoyage des données
│   ├── features/       # Feature engineering
│   ├── models/         # Entraînement (Hydra+MLflow) et prédiction
│   └── utils/           # Logger centralisé
├── api/                # FastAPI + schémas Pydantic
├── frontend/           # Application Streamlit + front React en bonus (react-app/)
├── tests/              # pytest (>= 70% de couverture sur src/)
├── docker/             # Dockerfile.api, Dockerfile.frontend, docker-compose.yml
├── .github/workflows/  # CI (lint, typage, tests, build Docker) + CD (bonus)
├── pyproject.toml
└── .pre-commit-config.yaml
```

Aucun écart par rapport à la structure imposée par le sujet.
