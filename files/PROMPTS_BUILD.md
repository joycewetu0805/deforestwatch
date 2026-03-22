# DeforestWatch-DRC — 25 Prompts de conception de A à Z

> **Mode d'emploi** : Exécute ces prompts dans l'ordre, un par un, dans une conversation Claude.
> Chaque prompt produit un livrable concret. Attache le README.md et le cahier des charges
> à la première conversation pour donner le contexte complet.

---

## PHASE 1 — FONDATIONS (Semaines 1–2)

### Prompt 1 : Configuration de l'environnement
```
Je travaille sur DeforestWatch-DRC, un projet Data Science de surveillance de la déforestation en RDC par imagerie satellite et ML. Voici mon README.md [attacher le fichier].

Génère-moi :
1. Le fichier config/settings.py avec toutes les variables d'environnement (GEE, Supabase, JWT, OpenWeather, zone d'étude Mai-Ndombe)
2. Le .env.example correspondant
3. Le requirements.txt complet avec toutes les dépendances versionnées
4. Le setup du projet avec __init__.py dans chaque dossier src/

Le code doit être complet, prêt à copier-coller dans VS Code.
```

### Prompt 2 : Connexion Google Earth Engine
```
Dans le cadre de DeforestWatch-DRC, crée le module src/data/gee_collector.py qui gère :
1. L'initialisation et l'authentification à Google Earth Engine
2. La définition de la zone d'étude (Mai-Ndombe, centre Inongo -1.95°S, 18.27°E, buffer 25km)
3. La récupération de la collection Sentinel-2 SR Harmonized filtrée par date, zone et couverture nuageuse
4. Le masquage des nuages via la bande SCL
5. Le calcul des indices spectraux : NDVI, EVI, NDWI, NBR
6. La création de composites annuels médians sur la saison sèche (juin-septembre) pour minimiser les nuages
7. La récupération du dataset Hansen Global Forest Change (ground truth)
8. La récupération des données SRTM (altitude, pente, aspect)

Inclus un __main__ qui teste chaque fonction. Code complet Python.
```

### Prompt 3 : Collecte météo et construction du dataset
```
Pour DeforestWatch-DRC, crée deux modules :

1. src/data/weather_collector.py :
   - Récupération des données météo historiques via OpenWeatherMap API pour la zone Mai-Ndombe
   - Précipitations mensuelles et température moyennes par année (2015-2025)
   - Stockage en DataFrame pandas

2. src/data/dataset_builder.py :
   - Combine les composites annuels GEE, les données Hansen, SRTM et météo
   - Exporte les données en format compatible ML (numpy arrays + CSV de métadonnées)
   - Crée deux datasets : un pixel-based (pour RF/XGBoost) et un tile-based 128x128 (pour U-Net)
   - Split train/val/test (70/15/15) avec stratification spatiale (éviter le data leakage géographique)

Code complet.
```

### Prompt 4 : Schema de base de données
```
Pour DeforestWatch-DRC, crée le module src/api/database.py avec SQLAlchemy pour PostgreSQL (Supabase) :

Tables nécessaires :
- users : id, email, password_hash, role (admin/user), otp_secret, created_at, is_active
- analysis_results : id, year, total_forest_ha, forest_loss_ha, deforestation_rate, model_used, created_at
- predictions : id, zone_lat, zone_lon, risk_score, predicted_year, model_version, created_at
- api_logs : id, user_id, endpoint, method, status_code, timestamp
- model_registry : id, model_name, version, accuracy, f1_score, mean_iou, file_path, deployed_at

Inclus les migrations Alembic (fichier de migration initial). Code complet.
```

---

## PHASE 2 — PRÉTRAITEMENT ET EDA (Semaines 3–4)

### Prompt 5 : Pipeline de prétraitement
```
Pour DeforestWatch-DRC, crée le package src/preprocessing/ avec :

1. cloud_masking.py : Masquage des nuages et ombres pour Sentinel-2 (bande SCL), calcul du pourcentage de pixels valides par image
2. indices.py : Calcul vectorisé des indices NDVI, EVI, NDWI, NBR à partir des bandes spectrales
3. mosaic.py : Création de mosaïques temporelles médianes par année (saison sèche juin-sept), gestion des images avec trop de nuages (> 70%)
4. feature_extraction.py :
   - Mode pixel : extrait un vecteur de features par pixel (6 bandes + 4 indices + altitude + pente + aspect = 13 features)
   - Mode tile : découpe l'image en tuiles 128x128 avec overlap de 32 pixels, normalise les bandes

Utilise numpy et rasterio. Optimise pour le traitement de grandes images. Code complet.
```

### Prompt 6 : Pipeline PySpark
```
Pour DeforestWatch-DRC, crée src/preprocessing/spark_pipeline.py :

Un pipeline PySpark qui :
1. Charge les features extraites (CSV pixel-based) dans un DataFrame Spark
2. Applique le nettoyage (suppression des pixels avec valeurs nulles/aberrantes)
3. Calcule des statistiques descriptives par année et par classe de couverture
4. Effectue le feature scaling (StandardScaler de PySpark ML)
5. Sauvegarde le dataset nettoyé en format Parquet partitionné par année

Ça doit justifier l'utilisation de Big Data pour le jury même si le dataset tient en mémoire. Code complet.
```

### Prompt 7 : Notebook EDA (Analyse Exploratoire)
```
Pour DeforestWatch-DRC, crée le notebook notebooks/01_exploration.ipynb en format .py (jupytext) que je convertirai en .ipynb.

Le notebook doit contenir :
1. Chargement et aperçu du dataset (shape, types, statistiques descriptives)
2. Distribution des classes de couverture du sol (bar chart + pourcentages)
3. Évolution temporelle de la couverture forestière 2015-2025 (line chart avec hectares)
4. Carte de la zone d'étude avec overlay de la couverture forestière (Folium)
5. Heatmap de corrélation entre les features (indices spectraux, altitude, pente)
6. Boxplots des indices NDVI/EVI par classe de couverture
7. Analyse de la distribution spatiale de la déforestation (quels secteurs perdent le plus)
8. Relation précipitations vs déforestation (scatter + corrélation)

Utilise Plotly pour les graphiques interactifs, Folium pour les cartes. Chaque cellule a un commentaire markdown explicatif.
```

### Prompt 8 : Notebook de prétraitement documenté
```
Pour DeforestWatch-DRC, crée notebooks/02_preprocessing.ipynb (format .py jupytext) :

1. Visualisation d'une image Sentinel-2 brute (RGB + fausses couleurs NIR)
2. Démonstration du masquage des nuages (avant/après)
3. Comparaison des indices spectraux sur une zone forêt vs zone déforestée
4. Visualisation d'une mosaïque annuelle complète
5. Distribution des features après extraction
6. Vérification du split train/val/test (pas de data leakage spatial)
7. Exemple de tuiles 128x128 pour le U-Net (grille visuelle)

Chaque étape illustrée visuellement avec des commentaires pédagogiques pour le mémoire.
```

---

## PHASE 3 — MODÉLISATION (Semaines 5–7)

### Prompt 9 : Modèle Random Forest
```
Pour DeforestWatch-DRC, crée src/models/random_forest.py :

1. Classe RandomForestClassifier wrapper avec :
   - Entraînement sur le dataset pixel-based (13 features → 5 classes)
   - Validation croisée 5-fold stratifiée
   - GridSearchCV pour l'optimisation des hyperparamètres (n_estimators, max_depth, min_samples_split)
   - Feature importance (quels indices spectraux sont les plus discriminants)
   - Sauvegarde du modèle avec joblib
   - Méthode predict() + predict_proba()

2. Fonction d'inférence : prend une image (array numpy) et retourne un masque de classification

Code complet avec logging. C'est le modèle baseline.
```

### Prompt 10 : Modèle XGBoost
```
Pour DeforestWatch-DRC, crée src/models/xgboost_model.py :

Même structure que le Random Forest mais avec XGBoost :
1. XGBClassifier avec les mêmes features (13 → 5 classes)
2. Validation croisée 5-fold
3. Optimisation des hyperparamètres (n_estimators, max_depth, learning_rate, subsample, colsample_bytree)
4. Feature importance (gain, weight, cover)
5. Early stopping sur le validation set
6. Sauvegarde/chargement du modèle

Code complet. Même interface que le RF pour faciliter la comparaison.
```

### Prompt 11 : Modèle U-Net (CNN)
```
Pour DeforestWatch-DRC, crée src/models/unet.py avec TensorFlow/Keras :

1. Architecture U-Net complète :
   - Encodeur : 4 blocs (Conv2D → BatchNorm → ReLU → MaxPool) avec filters [32, 64, 128, 256]
   - Bottleneck : 512 filters
   - Décodeur : 4 blocs (Conv2DTranspose → Concat skip → Conv2D → BatchNorm → ReLU)
   - Dropout 0.3 entre chaque bloc
   - Sortie : Conv2D 5 classes + softmax

2. Input : tuiles 128×128×6 (6 bandes spectrales)
3. Output : masque 128×128×5 (5 classes de couverture)
4. Data augmentation : rotation, flip horizontal/vertical, zoom
5. Callbacks : ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard
6. Méthode predict() qui reconstruit l'image complète à partir des tuiles

Code complet TensorFlow/Keras.
```

### Prompt 12 : Pipeline d'entraînement unifié
```
Pour DeforestWatch-DRC, crée src/models/trainer.py :

Un pipeline unifié qui :
1. Charge le dataset (pixel-based pour RF/XGBoost, tile-based pour U-Net)
2. Entraîne les 3 modèles séquentiellement
3. Évalue chaque modèle sur le test set
4. Logge les résultats avec loguru
5. Sauvegarde les modèles dans data/models/
6. Génère un rapport JSON avec toutes les métriques

Exécutable en une seule commande : python -m src.models.trainer
Code complet.
```

### Prompt 13 : Évaluateur et comparateur de modèles
```
Pour DeforestWatch-DRC, crée src/models/evaluator.py :

Classe ModelEvaluator qui :
1. Évalue un modèle avec : Accuracy, Precision, Recall, F1-Score (macro + par classe), AUC-ROC, IoU par classe, Mean IoU
2. Génère la matrice de confusion
3. Produit un tableau comparatif pandas des 3 modèles (RF vs XGBoost vs U-Net)
4. Identifie le meilleur modèle par métrique
5. Génère un rapport textuel formaté (pour le mémoire)
6. Exporte les résultats en JSON (pour le dashboard)

Code complet.
```

### Prompt 14 : Notebook de modélisation
```
Pour DeforestWatch-DRC, crée notebooks/03_modeling.ipynb (format .py jupytext) :

1. Entraînement des 3 modèles avec visualisation des courbes d'apprentissage
2. Tableau comparatif des performances (le tableau qui impressionne le jury)
3. Matrices de confusion pour chaque modèle (heatmaps)
4. Feature importance pour RF et XGBoost (bar charts comparés)
5. Visualisation de la segmentation U-Net : image originale → masque prédit → masque réel (grille côte à côte)
6. Carte de classification complète de la zone d'étude avec le meilleur modèle
7. Analyse des erreurs : où les modèles se trompent (carte des pixels mal classifiés)

Commentaires pédagogiques détaillés pour chaque section.
```

### Prompt 15 : Modèle de prédiction de risque
```
Pour DeforestWatch-DRC, crée src/models/risk_predictor.py :

Un modèle qui prédit les zones à risque de déforestation future :
1. Features de risque par pixel : distance à la route la plus proche, distance au village le plus proche, distance à la zone déjà déforestée, pente, altitude, taux de déforestation historique des pixels voisins
2. Modèle : Gradient Boosting (XGBoost) binaire — sera déforesté dans les 2 ans : oui/non
3. Ground truth : les pixels déforestés en 2023-2024 servent de labels positifs, entraînement sur données 2015-2022
4. Sortie : carte de risque (score 0-100) pour chaque pixel de la zone d'étude
5. Validation : vérifier que le modèle détecte effectivement les zones déforestées en 2023-2024

Code complet.
```

---

## PHASE 4 — DÉPLOIEMENT (Semaines 8–9)

### Prompt 16 : Backend FastAPI
```
Pour DeforestWatch-DRC, crée src/api/main.py et src/api/routes.py :

API FastAPI avec les endpoints :
- POST /api/v1/auth/register — inscription
- POST /api/v1/auth/login — connexion (retourne JWT)
- POST /api/v1/auth/verify-otp — vérification 2FA
- GET /api/v1/statistics — statistiques de déforestation par année
- GET /api/v1/predictions/{year} — carte de risque pour une année
- GET /api/v1/models — liste des modèles avec performances
- GET /api/v1/images/{year} — composite satellite pour une année donnée
- GET /api/v1/admin/users — liste des utilisateurs (admin only)
- GET /api/v1/admin/logs — logs d'utilisation (admin only)

Middleware CORS, documentation Swagger auto, gestion d'erreurs, logging des requêtes. Code complet.
```

### Prompt 17 : Authentification 2FA + JWT
```
Pour DeforestWatch-DRC, crée src/api/auth.py :

Système d'authentification complet :
1. Inscription avec hachage bcrypt du mot de passe
2. Login qui retourne un JWT (access token + refresh token)
3. Génération du secret OTP (PyOTP) à l'inscription
4. Endpoint de vérification OTP (compatible Google Authenticator)
5. Middleware de vérification JWT sur les routes protégées
6. Décorateur @require_role("admin") pour les routes admin
7. Refresh token pour renouveler les sessions expirées

Inclus les schemas Pydantic dans src/api/schemas.py. Code complet.
```

### Prompt 18 : Dashboard Streamlit principal
```
Pour DeforestWatch-DRC, crée streamlit_app/app.py et streamlit_app/pages/dashboard.py :

Dashboard principal avec :
1. Page de connexion (email + mot de passe + code OTP)
2. Sidebar avec navigation (Dashboard, Analyse, Prédictions, Admin)
3. Page Dashboard :
   - KPIs en haut : surface forestière actuelle, perte totale, taux de déforestation annuel
   - Carte interactive Folium avec couches togglables (couverture actuelle, zones déforestées, zones à risque)
   - Graphique d'évolution temporelle 2015-2025 (Plotly)
   - Top 5 zones les plus touchées

Design propre avec st.columns, st.metric, st.plotly_chart. Code complet Streamlit.
```

### Prompt 19 : Pages Analyse et Prédictions
```
Pour DeforestWatch-DRC, crée :

1. streamlit_app/pages/analysis.py :
   - Sélecteur d'année (slider)
   - Carte de couverture du sol pour l'année sélectionnée
   - Comparaison côte à côte de deux années
   - Graphiques de distribution des classes
   - Tableau comparatif des modèles ML (le fameux tableau)
   - Matrices de confusion interactives

2. streamlit_app/pages/prediction.py :
   - Carte de risque de déforestation (heatmap rouge/jaune/vert)
   - Filtre par niveau de risque (slider)
   - Statistiques : hectares à risque, pourcentage de la zone
   - Liste des zones critiques avec coordonnées

Code complet Streamlit, utilise Plotly et Folium.
```

### Prompt 20 : Backoffice administrateur
```
Pour DeforestWatch-DRC, crée streamlit_app/pages/admin.py :

Tableau de bord admin (accessible uniquement aux utilisateurs avec role="admin") :
1. Gestion des utilisateurs : tableau CRUD (créer, modifier rôle, désactiver)
2. Logs d'utilisation : tableau des dernières requêtes API avec filtres (date, utilisateur, endpoint)
3. Métriques d'utilisation : nombre de requêtes/jour (graphique), utilisateurs actifs
4. Gestion des modèles : liste des modèles déployés avec version, date, performances
5. Génération de rapports : bouton pour générer un PDF récapitulatif de la déforestation

Code complet Streamlit.
```

---

## PHASE 5 — FINALISATION (Semaines 10–12)

### Prompt 21 : Tests unitaires
```
Pour DeforestWatch-DRC, crée le dossier tests/ avec :

1. tests/test_preprocessing.py : teste le calcul des indices (NDVI, EVI), le masquage des nuages, la création de mosaïques (avec des données synthétiques numpy)
2. tests/test_models.py : teste l'entraînement et la prédiction de chaque modèle sur un mini-dataset, vérifie les shapes de sortie, les métriques
3. tests/test_api.py : teste chaque endpoint FastAPI avec httpx (inscription, login, OTP, statistiques, routes admin protégées)
4. tests/conftest.py : fixtures partagées (mini-dataset, client API test, utilisateur test)

Objectif : couverture > 70%. Code complet pytest.
```

### Prompt 22 : Docker
```
Pour DeforestWatch-DRC, crée :

1. Dockerfile : image Python 3.11-slim avec dépendances système (GDAL, libgeos), installation des requirements, expose ports 8000 (FastAPI) et 8501 (Streamlit)
2. docker-compose.yml : services app (FastAPI + Streamlit) et db (PostgreSQL 16), volumes pour data/ et config/, env_file .env
3. .dockerignore : exclure venv, __pycache__, data/raw, .git, notebooks

Les commandes pour build et run. Configuration testée et fonctionnelle.
```

### Prompt 23 : Scripts d'automatisation
```
Pour DeforestWatch-DRC, crée scripts/ avec :

1. scripts/collect_data.py : lance la collecte complète (GEE + météo) pour toutes les années
2. scripts/train_all.py : lance le pipeline d'entraînement complet (preprocessing → training → evaluation)
3. scripts/backup_db.py : sauvegarde PostgreSQL (pg_dump)
4. scripts/generate_report.py : génère un rapport PDF avec les dernières statistiques et prédictions
5. Makefile : commandes make collect, make train, make test, make deploy, make backup

Code complet, chaque script exécutable en standalone.
```

### Prompt 24 : Notebook de résultats final
```
Pour DeforestWatch-DRC, crée notebooks/04_results.ipynb (format .py jupytext) :

Le notebook de synthèse pour le mémoire :
1. Résumé exécutif : principales conclusions en 5 points
2. Carte finale de couverture du sol 2025 (le résultat principal)
3. Timeline de la déforestation 2015-2025 avec annotation des événements clés
4. Tableau comparatif final des 3 modèles avec analyse critique (pourquoi le meilleur est le meilleur)
5. Carte de risque de déforestation future avec zones prioritaires
6. Limites identifiées et pistes d'amélioration
7. Figures de qualité publication (300 DPI, polices propres) exportables pour le mémoire

Tout en français. Prêt à être inclus dans le rapport final.
```

### Prompt 25 : Structure du mémoire
```
Pour mon projet DeforestWatch-DRC (Data Science, L3 UPC), génère la structure complète du mémoire en Word (.docx) avec :

1. Page de garde (UPC, FASI, titre, auteur, directeur, année)
2. Table des matières
3. Liste des figures et tableaux
4. Sigles et abréviations
5. Introduction générale (contexte, problématique, objectifs, méthodologie, plan)
6. Chapitre 1 : Revue de la littérature (déforestation en RDC, télédétection, ML pour la classification d'images satellites, U-Net)
7. Chapitre 2 : Méthodologie (zone d'étude, données, prétraitement, architecture technique, modèles)
8. Chapitre 3 : Résultats et discussion (EDA, comparaison des modèles, carte de risque, analyse critique)
9. Chapitre 4 : Implémentation (stack technique, API, dashboard, authentification, tests, Docker)
10. Conclusion générale et perspectives
11. Bibliographie
12. Annexes (code source, captures d'écran, configurations)

Génère le document Word avec la structure, les titres formatés, et des indications de contenu pour chaque section (1-2 phrases décrivant ce qu'il faut écrire).
```

---

## BONUS — Prompts complémentaires si nécessaire

### Prompt 26 : Présentation PowerPoint de soutenance
```
Crée une présentation PowerPoint de soutenance pour DeforestWatch-DRC (15-20 slides) :
Slide 1: Titre, Slide 2: Problématique, Slide 3: Objectifs, Slide 4: Zone d'étude (carte),
Slide 5-6: Données et sources, Slide 7: Architecture technique, Slide 8: Prétraitement,
Slide 9-10: Modèles ML (RF, XGBoost, U-Net), Slide 11: Tableau comparatif des résultats,
Slide 12: Carte de classification, Slide 13: Carte de risque, Slide 14: Dashboard (capture),
Slide 15: Déploiement (Docker, API), Slide 16: Limites, Slide 17: Perspectives, Slide 18: Merci.
Design professionnel, couleurs cohérentes, peu de texte par slide.
```

### Prompt 27 : Déploiement Streamlit Cloud + Render
```
Guide-moi étape par étape pour déployer DeforestWatch-DRC :
1. Le dashboard Streamlit sur Streamlit Community Cloud (gratuit)
2. L'API FastAPI sur Render (free tier)
3. La base PostgreSQL sur Supabase (déjà configuré)
4. Les variables d'environnement à configurer sur chaque plateforme
5. Le fichier streamlit secrets.toml
6. Les modifications de code nécessaires pour la production (URLs, CORS, debug off)
```
