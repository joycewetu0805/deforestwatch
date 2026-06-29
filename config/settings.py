"""
DeforestWatch-DRC — Configuration centralisée
Toutes les variables d'environnement et constantes du projet.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path

# Racine du projet (config/ -> ..)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"


class Settings(BaseSettings):
    """Configuration chargée depuis .env"""

    # ── Google Earth Engine ──
    gee_service_account: Optional[str] = None
    gee_key_file: str = "config/gee-key.json"

    # ── Database ──
    database_url: str = "postgresql://postgres:deforestwatch_dev@localhost:5432/deforestwatch"
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # ── OpenWeatherMap ──
    openweather_api_key: Optional[str] = None

    # ── Authentication ──
    jwt_secret_key: str = "change-this-in-production-with-a-long-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # ── App ──
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000
    streamlit_port: int = 8501

    # Mode démo : utilise des données synthétiques (aucune dépendance externe)
    demo_mode: bool = True

    # ── Zone d'étude ──
    study_area_lat: float = -1.95       # Inongo, Mai-Ndombe
    study_area_lon: float = 18.27
    study_area_buffer_km: int = 25      # Rayon 25km → zone ~50km x 50km

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# ── Constantes du projet ──

# Bandes spectrales Sentinel-2 utilisées
SENTINEL2_BANDS = {
    "B2": "Blue (490nm)",
    "B3": "Green (560nm)",
    "B4": "Red (665nm)",
    "B8": "NIR (842nm)",
    "B11": "SWIR1 (1610nm)",
    "B12": "SWIR2 (2190nm)",
}
BAND_ORDER = ["B2", "B3", "B4", "B8", "B11", "B12"]

# Indices spectraux
SPECTRAL_INDICES = {
    "NDVI": "(NIR - Red) / (NIR + Red)",       # Végétation
    "EVI": "2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)",  # Végétation amélioré
    "NDWI": "(Green - NIR) / (Green + NIR)",    # Eau
    "NBR": "(NIR - SWIR2) / (NIR + SWIR2)",    # Brûlis
}
INDEX_ORDER = ["NDVI", "EVI", "NDWI", "NBR"]

# Features topographiques (SRTM)
TOPO_FEATURES = ["altitude", "slope", "aspect"]

# Ordre complet des features pour le modèle pixel-based (13 features)
FEATURE_NAMES = BAND_ORDER + INDEX_ORDER + TOPO_FEATURES

# Écosystème ciblé — le projet est recentré sur la forêt équatoriale
ECOSYSTEM = "Forêt tropicale humide équatoriale — Bassin du Congo (Mai-Ndombe, RDC)"

# Classes de couverture du sol
LAND_COVER_CLASSES = {
    0: "Forêt dense",
    1: "Forêt dégradée",
    2: "Agriculture / Sol nu",
    3: "Eau",
    4: "Zone urbaine / Bâti",
}
NUM_CLASSES = len(LAND_COVER_CLASSES)
CLASS_COLORS = {
    0: "#0B6E2D",   # vert forêt
    1: "#9BCC4F",   # vert clair dégradé
    2: "#D9A441",   # ocre agriculture
    3: "#2E86C1",   # bleu eau
    4: "#C0392B",   # rouge bâti
}

# Période d'analyse
ANALYSIS_START_YEAR = 2015
ANALYSIS_END_YEAR = 2025
ANALYSIS_YEARS = list(range(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR + 1))

# Résolution de la grille synthétique de la zone d'étude (pixels)
GRID_SIZE = 256          # 256x256 pixels pour la zone ~50km
PIXEL_AREA_HA = (50_000 / GRID_SIZE) ** 2 / 10_000  # surface d'un pixel en hectares

# Paramètres des modèles ML (defaults)
RF_PARAMS = {
    "n_estimators": 200,
    "max_depth": 15,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": 42,
    "n_jobs": -1,
}

XGB_PARAMS = {
    "n_estimators": 200,
    "max_depth": 10,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
}

UNET_PARAMS = {
    "input_shape": (128, 128, 6),   # 6 bandes spectrales
    "num_classes": 5,                # 5 classes de couverture
    "filters": [32, 64, 128, 256],
    "batch_size": 16,
    "epochs": 50,
    "learning_rate": 1e-4,
}


# Instance globale
settings = Settings()
