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


def risk_map() -> np.ndarray:
    """Carte de risque calculée sur la source active."""
    return synthetic.risk_map(series=landcover_series())


def info() -> dict:
    return describe_source()
