"""
DeforestWatch-DRC — Configuration centralisée
Toutes les variables d'environnement et constantes du projet.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

# Racine du projet (config/ -> ..)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

# Valeur par défaut du secret JWT — volontairement reconnaissable pour que la
# validation de production puisse détecter qu'elle n'a pas été surchargée.
DEFAULT_JWT_SECRET = "change-this-in-production-with-a-long-random-secret-key"


class Settings(BaseSettings):
    """Configuration chargée depuis .env"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

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
    jwt_secret_key: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # ── 2FA (imposée côté serveur) ──
    require_2fa: bool = True             # exiger le code OTP à la connexion
    demo_otp_code: str = "123456"        # code statique accepté en mode démo

    # ── Bootstrap admin en production (optionnel, via variables d'env) ──
    admin_email: Optional[str] = None
    admin_password: Optional[str] = None

    # ── CORS ── liste d'origines séparées par des virgules ; "*" = tout (dev)
    cors_origins: str = "*"

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

    # ── Notifications e-mail (SMTP) des alertes ──
    alert_email_enabled: bool = False   # sécurité : désactivé par défaut
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    alert_email_from: Optional[str] = None
    alert_email_to: Optional[str] = None  # destinataires séparés par des virgules

    # ── Helpers ──
    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in ("production", "prod")

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def production_config_problems(s: "Settings") -> list[str]:
    """Retourne la liste des réglages dangereux si l'on tourne en production.

    Sert au « fail-fast » : une instance de production ne doit pas démarrer avec
    le secret JWT par défaut, le debug actif ou un CORS grand ouvert.
    """
    if not s.is_production:
        return []
    problems: list[str] = []
    if s.jwt_secret_key == DEFAULT_JWT_SECRET:
        problems.append("JWT_SECRET_KEY est resté à sa valeur par défaut")
    if s.app_debug:
        problems.append("APP_DEBUG=true en production")
    if "*" in s.cors_origins_list():
        problems.append("CORS_ORIGINS ouvert à toutes les origines (*)")
    if s.demo_mode:
        problems.append("DEMO_MODE=true en production (compte admin de démo créé)")
    return problems


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

# Bandes radar Sentinel-1 (rétrodiffusion, dB) — pénètrent les nuages
SENTINEL1_BANDS = {
    "VV": "Rétrodiffusion co-polarisée (dB)",
    "VH": "Rétrodiffusion cross-polarisée (dB)",
}
RADAR_BAND_ORDER = ["VV", "VH"]

# ── Estimation du carbone ──
# Biomasse aérienne moyenne d'une forêt tropicale humide dense du Bassin du Congo.
# Valeur médiane de la littérature (~310 t/ha de biomasse sèche).
AGB_TONNES_PER_HA = 310.0            # biomasse aérienne (t/ha)
CARBON_FRACTION = 0.47              # fraction de carbone dans la biomasse (IPCC)
CO2_PER_CARBON = 44.0 / 12.0        # conversion C -> CO2 (~3.67)
# Facteur direct : tonnes de CO2 émises par hectare de forêt détruite
CO2_TONNES_PER_HA = AGB_TONNES_PER_HA * CARBON_FRACTION * CO2_PER_CARBON

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
