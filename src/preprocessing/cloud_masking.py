"""
Masquage des nuages et ombres pour Sentinel-2 (basé sur la bande SCL).
Inclut le calcul du pourcentage de pixels valides par image.
"""

from __future__ import annotations

import numpy as np

# Codes SCL Sentinel-2 considérés invalides : ombres, nuages, neige, no-data
INVALID_SCL = {0, 1, 3, 8, 9, 10, 11}


def cloud_mask_from_scl(scl: np.ndarray) -> np.ndarray:
    """Renvoie un masque booléen True = pixel valide (sans nuage)."""
    mask = np.ones_like(scl, dtype=bool)
    for code in INVALID_SCL:
        mask &= scl != code
    return mask


def apply_mask(bands: np.ndarray, mask: np.ndarray, fill: float = np.nan) -> np.ndarray:
    """Applique le masque sur un array de bandes (H,W,B)."""
    out = bands.astype(np.float32).copy()
    out[~mask] = fill
    return out


def valid_fraction(mask: np.ndarray) -> float:
    """Pourcentage de pixels valides (0..100)."""
    return float(100.0 * mask.mean())


def synthetic_scl(shape, cloud_fraction: float = 0.2, seed: int = 0) -> np.ndarray:
    """Génère une bande SCL synthétique avec une couverture nuageuse donnée."""
    rng = np.random.default_rng(seed)
    scl = np.full(shape, 4, dtype=np.int16)  # 4 = végétation (valide)
    clouds = rng.random(shape) < cloud_fraction
    scl[clouds] = 9  # nuage
    return scl
