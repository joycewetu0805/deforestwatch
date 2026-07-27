"""
Point d'accès unifié aux données (synthétiques ou réelles).

Tout le code applicatif (datasets ML, statistiques, dashboard, API) importe
ces fonctions plutôt que d'appeler directement le générateur synthétique.
Ainsi, déposer de vraies images dans data/raw/ et mettre DEMO_MODE=false
bascule automatiquement toute l'application sur les données réelles.
"""

from __future__ import annotations

import numpy as np

from src.data.sources import (
    current_mode,
    describe_source,
    real_data_available,
    resolve_source,
    set_mode,
)
from src.utils import synthetic
from src.utils.logger import get_logger

log = get_logger("provider")


def source():
    return resolve_source()


def source_name() -> str:
    return source().name


def is_real() -> bool:
    return source().is_real


def mode() -> str:
    """Mode demandé : 'demo', 'real' ou 'auto'."""
    return current_mode()


def switch(mode_name: str | None) -> str:
    """Bascule le mode de données à l'exécution. Renvoie le mode effectif."""
    return set_mode(mode_name)


def has_real_data() -> bool:
    return real_data_available()


def years() -> list[int]:
    return source().years()


def composite(year: int) -> np.ndarray:
    return source().composite(year)


def topography() -> np.ndarray:
    return source().topography()


def landcover_series() -> dict[int, np.ndarray]:
    """Série {année: carte de classes}. Pour la source synthétique, série complète."""
    src = source()
    series = src.landcover_series()
    if not series:  # source réelle sans étiquettes → repli synthétique pour l'affichage
        return synthetic.generate_landcover_series()
    return series


def yearly_statistics() -> list[dict]:
    """Statistiques de déforestation calculées sur la source active."""
    return synthetic.yearly_statistics(series=landcover_series())


# Modèle de risque chargé une seule fois, puis réutilisé.
_risk_model = None
_risk_model_loaded = False


def _load_risk_model():
    """Charge le prédicteur entraîné, ou None s'il n'a pas encore été entraîné."""
    global _risk_model, _risk_model_loaded
    if _risk_model_loaded:
        return _risk_model
    _risk_model_loaded = True
    try:
        from src.models import risk_predictor

        if risk_predictor.is_trained():
            _risk_model = risk_predictor.RiskPredictor.load()
            log.info("Carte de risque : modèle entraîné chargé.")
        else:
            log.warning(
                "Aucun modèle de risque entraîné dans data/models/ : repli sur "
                "la référence géométrique. Lancez `make train` pour utiliser le "
                "modèle appris."
            )
    except Exception as exc:  # pragma: no cover - dépend de l'install ML
        log.warning(f"Modèle de risque illisible ({exc}) : repli géométrique.")
        _risk_model = None
    return _risk_model


def risk_source() -> str:
    """Origine de la carte de risque : 'model' (appris) ou 'baseline' (géométrique)."""
    return "model" if _load_risk_model() is not None else "baseline"


def risk_source_label() -> str:
    """Libellé affichable de l'origine de la carte de risque."""
    return ("Prédicteur entraîné (XGBoost, 6 variables d'accessibilité)"
            if risk_source() == "model"
            else "Référence géométrique (décroissance avec la distance au front)")


def risk_map() -> np.ndarray:
    """
    Carte de risque calculée sur la source active.

    Utilise le modèle entraîné s'il est disponible sur le disque. Sinon, replie
    sur la référence géométrique, qui ne demande aucun entraînement. Les deux
    renvoient une grille 0..100 de même forme, donc l'appelant n'a rien à
    changer ; `risk_source()` indique laquelle est active.
    """
    model = _load_risk_model()
    series = landcover_series()
    if model is None:
        return synthetic.risk_map(series=series)
    try:
        return model.risk_map(series=series)
    except Exception as exc:  # pragma: no cover - robustesse à la démo
        log.warning(f"Prédiction du modèle en échec ({exc}) : repli géométrique.")
        return synthetic.risk_map(series=series)


def reset_risk_model() -> None:
    """Force le rechargement du modèle au prochain appel (après un entraînement)."""
    global _risk_model, _risk_model_loaded
    _risk_model, _risk_model_loaded = None, False


def info() -> dict:
    return describe_source()
