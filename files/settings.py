"""
DeforestWatch-DRC — Configuration centralisée
Toutes les variables d'environnement et constantes du projet.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Configuration chargée depuis .env"""

    # ── Google Earth Engine ──
    gee_service_account: Optional[str] = None
    gee_key_file: str = "config/gee-key.json"

    # ── Database ──
    database_url: str = "postgresql://localhost:5432/deforestwatch"
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # ── OpenWeatherMap ──
    openweather_api_key: Optional[str] = None

    # ── Authentication ──
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # ── App ──
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000
    streamlit_port: int = 8501

    # ── Zone d'étude ──
    study_area_lat: float = -1.95       # Inongo, Mai-Ndombe
    study_area_lon: float = 18.27
    study_area_buffer_km: int = 25      # Rayon 25km → zone ~50km x 50km

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


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

# Indices spectraux
SPECTRAL_INDICES = {
    "NDVI": "(NIR - Red) / (NIR + Red)",       # Végétation
    "EVI": "2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)",  # Végétation amélioré
    "NDWI": "(Green - NIR) / (Green + NIR)",    # Eau
    "NBR": "(NIR - SWIR2) / (NIR + SWIR2)",    # Brûlis
}

# Classes de couverture du sol
LAND_COVER_CLASSES = {
    0: "Forêt dense",
    1: "Forêt dégradée",
    2: "Agriculture / Sol nu",
    3: "Eau",
    4: "Zone urbaine / Bâti",
}

# Période d'analyse
ANALYSIS_START_YEAR = 2015
ANALYSIS_END_YEAR = 2025

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
