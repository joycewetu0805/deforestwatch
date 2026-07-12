# 🌍 DeforestWatch-DRC

**Surveillance et prédiction de la déforestation de la forêt équatoriale du Bassin du Congo (RDC) par imagerie satellite et Machine Learning**

> 🌳 **Écosystème ciblé** : forêt tropicale humide **équatoriale** du Bassin du Congo (province du Mai-Ndombe).

![CI](https://github.com/joycewetu0805/deforestwatch/actions/workflows/ci.yml/badge.svg)

> 📘 **Guide complet & mode d'emploi** : [`GUIDE.md`](GUIDE.md) (ou `docs/GUIDE.pdf`) —
> tout le projet expliqué pas à pas, dont le téléchargement des données depuis Google Earth Engine.
>
> 🌍 **Impact & plus-value (contexte congolais)** : [`IMPACT.md`](IMPACT.md) —
> à quoi sert concrètement la plateforme, et pour qui.

Projet de fin d'études — L3 LMD FASI, Université Protestante au Congo  
Orientation : Data Science  
Auteur : Joyce A. WETUNGANI
Date : 2026

---

## Problématique

La RDC abrite la deuxième plus grande forêt tropicale du monde. Chaque année, des milliers d'hectares disparaissent sous l'effet de l'agriculture sur brûlis, de l'exploitation forestière et de l'expansion urbaine. Les outils de surveillance existants (Global Forest Watch, etc.) fournissent des données globales mais ne proposent pas d'analyse prédictive locale adaptée au contexte congolais.

**DeforestWatch-DRC** est une plateforme d'analyse et de prédiction de la déforestation qui exploite les images satellites Sentinel-2 et Landsat, combinées à des techniques de Machine Learning et de Computer Vision, pour :

- Détecter les zones déforestées sur une région cible du bassin du Congo
- Quantifier la perte forestière année par année (2015–2025)
- Prédire les zones à risque de déforestation future
- Fournir un dashboard interactif d'aide à la décision

## Zone d'étude

**Province du Mai-Ndombe** — l'un des fronts de déforestation les plus actifs en RDC, avec une pression croissante liée à l'agriculture itinérante et aux concessions forestières. Zone de travail : ~50km × 50km autour de la ville d'Inongo.

## Architecture technique

```
┌──────────────────────────────────────────────────────┐
│                  COLLECTE DE DONNÉES                  │
│  Google Earth Engine │ Sentinel-2 │ Landsat │ Météo  │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│              PRÉTRAITEMENT (PySpark)                   │
│  Mosaïques │ Correction atmosphérique │ NDVI/EVI     │
│  Masquage nuages │ Normalisation │ Feature extraction │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│              MODÉLISATION (Scikit-learn / TensorFlow)  │
│  Random Forest │ XGBoost │ U-Net (CNN)                │
│  Validation croisée │ Comparaison métriques           │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│              DÉPLOIEMENT                               │
│  FastAPI (backend) │ Streamlit (dashboard)            │
│  PostgreSQL (stockage) │ Auth 2FA │ Admin panel       │
└──────────────────────────────────────────────────────┘
```

## Stack technique

| Composant | Technologie |
|---|---|
| Langage principal | Python 3.11+ |
| Collecte satellite | Google Earth Engine (Python API), `earthengine-api` |
| Prétraitement | PySpark, Rasterio, GDAL |
| Indices spectraux | NDVI, EVI, NDWI via `rasterio` / GEE |
| ML classique | Scikit-learn (Random Forest, XGBoost) |
| Deep Learning | TensorFlow/Keras (U-Net segmentation) |
| Visualisation | Streamlit, Plotly, Matplotlib, Seaborn, Folium |
| Backend API | FastAPI |
| Base de données | PostgreSQL (Supabase) |
| Authentification | PyOTP (2FA), JWT |
| Big Data | PySpark |
| Versioning | Git + GitHub |
| Containerisation | Docker + docker-compose |
| Tests | pytest |

## Structure du projet

```
deforest-watch/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── config/
│   └── settings.py              # Configuration centralisée
├── src/
│   ├── data/
│   │   ├── gee_collector.py     # Collecte via Google Earth Engine
│   │   ├── weather_collector.py # Données météorologiques
│   │   └── dataset_builder.py   # Construction du dataset final
│   ├── preprocessing/
│   │   ├── cloud_masking.py     # Masquage des nuages
│   │   ├── indices.py           # Calcul NDVI, EVI, NDWI
│   │   ├── mosaic.py            # Composition de mosaïques temporelles
│   │   └── feature_extraction.py# Extraction des features pour ML
│   ├── models/
│   │   ├── random_forest.py     # Modèle Random Forest
│   │   ├── xgboost_model.py     # Modèle XGBoost
│   │   ├── unet.py              # Architecture U-Net (CNN)
│   │   ├── trainer.py           # Pipeline d'entraînement
│   │   └── evaluator.py         # Comparaison des modèles
│   ├── visualization/
│   │   ├── maps.py              # Cartes interactives (Folium)
│   │   ├── charts.py            # Graphiques (Plotly)
│   │   └── timeline.py          # Évolution temporelle
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── auth.py              # Authentification 2FA + JWT
│   │   ├── routes.py            # Endpoints API RESTful
│   │   └── schemas.py           # Modèles Pydantic
│   └── utils/
│       ├── logger.py            # Logging centralisé
│       └── helpers.py           # Fonctions utilitaires
├── notebooks/                   # Notebooks au format script (.py, jupytext)
│   ├── 01_exploration.py        # EDA initiale
│   ├── 02_preprocessing.py      # Pipeline de prétraitement
│   ├── 03_modeling.py           # Entraînement et comparaison
│   └── 04_results.py            # Résultats et visualisations
├── streamlit_app/
│   ├── app.py                   # Dashboard principal (login 2FA + navigation)
│   ├── views/                   # Pages (dossier nommé "views" pour ne pas
│   │   ├── dashboard.py         #  déclencher le multipage auto de Streamlit)
│   │   ├── analysis.py          # Analyse exploratoire
│   │   ├── prediction.py        # Prédictions
│   │   └── admin.py             # Backoffice admin
│   └── components/
│       └── auth.py              # Composant d'authentification
├── frontend/                    # Frontend React (CongoForest Watch)
│   ├── package.json             # Vite + React + Tailwind
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── LandingPage.jsx  # Landing page animée
│           └── Dashboard.jsx    # Monitoring (fetch API + repli statique)
├── scripts/                     # Automatisation (seed, collect, train, report)
├── tests/
│   ├── test_preprocessing.py
│   ├── test_models.py
│   └── test_api.py
├── data/
│   ├── raw/                     # Données brutes (non versionné)
│   ├── processed/               # Données traitées
│   └── models/                  # Modèles sauvegardés
└── docs/                        # Livrables générés
    ├── memoire_deforestwatch.docx
    ├── soutenance_deforestwatch.pptx
    └── GUIDE.pdf
```

## Installation et lancement

### Prérequis

- Python 3.11+
- Compte Google Earth Engine (gratuit pour usage académique)
- Docker (optionnel, pour le déploiement)

### Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/joycewetu0805/deforestwatch.git
cd deforestwatch

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Remplir les variables dans .env

# Authentification Google Earth Engine
earthengine authenticate
```

### Démarrage rapide — mode démo (sans Google Earth Engine)

Le projet fonctionne **clé en main** grâce à un mode démo (`DEMO_MODE=true`) qui
génère des données satellites synthétiques réalistes. Aucune clé API ni compte
GEE n'est requis pour faire tourner l'API, le dashboard et les modèles.

```bash
pip install -r requirements.txt
make seed        # génère datasets synthétiques + entraîne les modèles
make api         # API FastAPI       → http://localhost:8000/docs
make dashboard   # Dashboard Streamlit → http://localhost:8501
make frontend    # Frontend React     → http://localhost:5173
```

Comptes de démonstration du dashboard :
- **admin@deforestwatch.cd** / `admin123` — code 2FA : `123456`
- **user@deforestwatch.cd** / `user123` — code 2FA : `123456`

### Lancement (détail)

```bash
# Backend API
uvicorn src.api.main:app --reload --port 8000

# Dashboard Streamlit
streamlit run streamlit_app/app.py --server.port 8501

# Frontend React
cd frontend && npm install && npm run dev

# Tests
pytest tests/ -v --cov=src
```

> **Passage en production** : renseignez les clés dans `.env`
> (GEE, Supabase, OpenWeather, JWT) et mettez `DEMO_MODE=false`. Les modules de
> collecte basculent automatiquement sur les vraies sources (Sentinel-2, Hansen,
> SRTM, OpenWeatherMap) et la base sur PostgreSQL/Supabase.

### Sécurité

- **2FA imposée côté serveur** : `/api/v1/auth/login` n'émet **aucun** token sans
  code OTP valide. En mode démo, le code statique `123456` est accepté ; en
  production, c'est un vrai code TOTP (Google Authenticator). Réglable via
  `REQUIRE_2FA`.
- **Fail-fast production** : avec `APP_ENV=production`, l'API **refuse de démarrer**
  si le secret JWT est resté par défaut, si `APP_DEBUG=true`, si le CORS est ouvert
  à `*` ou si `DEMO_MODE=true`.
- **CORS** : origines autorisées via `CORS_ORIGINS` (liste séparée par des virgules).
- **Compte admin** : en démo, `admin@deforestwatch.cd` / `admin123` est créé
  automatiquement. En production, aucun compte par défaut : renseignez
  `ADMIN_EMAIL` / `ADMIN_PASSWORD` pour bootstrapper un admin.

### Brancher de vraies images satellites

Le projet est conçu pour passer des données de démonstration aux **vraies
images** sans modifier le code. Une couche d'abstraction (`src/data/sources.py`)
résout automatiquement la source active :

1. Déposez vos GeoTIFF dans `data/raw/` selon le format décrit dans
   [`data/raw/README.md`](data/raw/README.md) (composites 6 bandes par année,
   cartes de classes optionnelles, topographie).
2. Vérifiez le jeu de données : `make check-data`.
3. Mettez `DEMO_MODE=false` dans `.env`.

Toute l'application (datasets ML, statistiques, dashboard, API `/api/v1/source`)
bascule alors sur les données réelles. Vous pouvez commencer avec **une seule
année** pour valider la chaîne, puis enrichir progressivement.

**Basculer démo ↔ réel** — trois façons, de la plus simple à la plus permanente :

| Méthode | Commande / action | Portée |
|---|---|---|
| 🖱️ Toggle dashboard | Barre latérale → « Source de données » (Auto / Démo / Réelle) | Bascule **à chaud**, sans redémarrer |
| 🔌 API (admin) | `POST /api/v1/admin/source/{auto\|demo\|real}` | Process API en cours |
| 💾 Persistant (`.env`) | `make demo` · `make real` · `make mode` | Tous les démarrages suivants |

Le mode **Auto** choisit automatiquement : données réelles si présentes dans
`data/raw/`, sinon démo. Si vous demandez « réel » sans données disponibles,
l'application fait un **repli transparent** sur la démo.

**Collecte des vraies images** via `scripts/gee_export.py` :

```bash
# Export Sentinel-2 depuis Google Earth Engine vers Google Drive (production)
python -m scripts.gee_export --drive
# ... ou téléchargement direct (zone réduite, aperçu)
python -m scripts.gee_export --download --scale 100

# Tester toute la chaîne réelle SANS compte GEE (écrit des GeoTIFF synthétiques)
make export-demo && make check-data
```

### Mémoire académique

```bash
make memoir      # génère docs/memoire_deforestwatch.docx (UPC/FASI)
make slides      # génère docs/soutenance_deforestwatch.pptx (16 slides)
```

Le mémoire (page de garde, chapitres, tableaux, bibliographie, annexes) et la
présentation de soutenance sont pré-remplis à partir du projet réellement
implémenté ; les résultats chiffrés sont à confirmer sur données réelles.

### Docker

```bash
docker-compose up --build
```

## Données utilisées

| Source | Description | Résolution | Couverture |
|---|---|---|---|
| Sentinel-2 (ESA) | Images multispectrales | 10m | 2015–présent |
| Landsat 8/9 (NASA) | Images multispectrales | 30m | 2013–présent |
| Hansen Global Forest Change | Perte forestière annuelle | 30m | 2000–2023 |
| OpenWeatherMap | Données météo (précipitations, température) | — | Temps réel |
| SRTM | Modèle numérique de terrain (altitude, pente) | 30m | Global |

## Modèles implémentés

1. **Random Forest** — Classification pixel par pixel à partir des indices spectraux (NDVI, EVI, NDWI) et données topographiques. Baseline solide et interprétable.

2. **XGBoost** — Gradient boosting sur les mêmes features. Comparaison directe avec Random Forest pour mesurer le gain de performance.

3. **U-Net (CNN)** — Segmentation sémantique prenant les bandes spectrales brutes en entrée. Détecte des patterns spatiaux que les modèles pixel-à-pixel ne capturent pas.

### Métriques de comparaison

- Accuracy, Precision, Recall, F1-Score
- AUC-ROC
- IoU (Intersection over Union) pour la segmentation
- Matrice de confusion

## Licence

Ce projet est réalisé dans un cadre académique. Les données satellites utilisées sont libres d'accès (ESA Copernicus, NASA/USGS).

## Contact

Joyce A. WETUNGANI — Université Protestante au Congo, FASI L3 LMD
