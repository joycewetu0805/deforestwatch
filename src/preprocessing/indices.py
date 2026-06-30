"""
Calcul vectorisé des indices spectraux NDVI, EVI, NDWI, NBR.
Entrée : array de bandes (H, W, 6) = [B2, B3, B4, B8, B11, B12].
"""

from __future__ import annotations

import numpy as np

EPS = 1e-6


def _bands(arr: np.ndarray):
    return [arr[..., i] for i in range(6)]  # B2,B3,B4,B8,B11,B12


def ndvi(arr: np.ndarray) -> np.ndarray:
    B2, B3, B4, B8, B11, B12 = _bands(arr)
    return (B8 - B4) / (B8 + B4 + EPS)


def evi(arr: np.ndarray) -> np.ndarray:
    B2, B3, B4, B8, B11, B12 = _bands(arr)
    return 2.5 * (B8 - B4) / (B8 + 6 * B4 - 7.5 * B2 + 1 + EPS)


def ndwi(arr: np.ndarray) -> np.ndarray:
    B2, B3, B4, B8, B11, B12 = _bands(arr)
    return (B3 - B8) / (B3 + B8 + EPS)


def nbr(arr: np.ndarray) -> np.ndarray:
    B2, B3, B4, B8, B11, B12 = _bands(arr)
    return (B8 - B12) / (B8 + B12 + EPS)


def all_indices(arr: np.ndarray) -> np.ndarray:
    """Empile les 4 indices en (H, W, 4) dans l'ordre NDVI, EVI, NDWI, NBR."""
    return np.stack([ndvi(arr), evi(arr), ndwi(arr), nbr(arr)], axis=-1).astype(np.float32)
