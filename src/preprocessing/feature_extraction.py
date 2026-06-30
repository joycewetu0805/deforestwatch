"""
Extraction des features pour le ML.

  - Mode pixel : un vecteur 13-D par pixel
        6 bandes + 4 indices (NDVI,EVI,NDWI,NBR) + altitude + pente + aspect
  - Mode tile  : tuiles 128x128 avec overlap de 32 px, bandes normalisées
"""

from __future__ import annotations

import numpy as np

from src.preprocessing.indices import all_indices


def extract_pixel_features(bands: np.ndarray, topo: np.ndarray) -> np.ndarray:
    """
    bands : (H,W,6), topo : (H,W,3) -> features (H*W, 13).
    """
    idx = all_indices(bands)
    feats = np.concatenate([bands, idx, topo], axis=-1)  # (H,W,13)
    return feats.reshape(-1, feats.shape[-1])


def normalize_bands(bands: np.ndarray) -> np.ndarray:
    """Normalisation min-max par bande sur l'array (H,W,B)."""
    out = bands.astype(np.float32).copy()
    for b in range(out.shape[-1]):
        lo, hi = np.nanmin(out[..., b]), np.nanmax(out[..., b])
        out[..., b] = (out[..., b] - lo) / (hi - lo + 1e-6)
    return out


def extract_tiles(bands: np.ndarray, labels: np.ndarray | None = None,
                  tile: int = 128, overlap: int = 32):
    """
    Découpe une image (H,W,B) en tuiles tile×tile avec recouvrement.
    Renvoie (tiles, [label_tiles], positions).
    """
    bands = normalize_bands(bands)
    H, W = bands.shape[:2]
    step = tile - overlap
    tiles, lab_tiles, positions = [], [], []
    for r in range(0, max(H - tile + 1, 1), step):
        for c in range(0, max(W - tile + 1, 1), step):
            r2, c2 = min(r + tile, H), min(c + tile, W)
            r0, c0 = r2 - tile, c2 - tile
            tiles.append(bands[r0:r2, c0:c2, :])
            if labels is not None:
                lab_tiles.append(labels[r0:r2, c0:c2])
            positions.append((r0, c0))
    tiles = np.array(tiles, dtype=np.float32)
    if labels is not None:
        return tiles, np.array(lab_tiles, dtype=np.int8), positions
    return tiles, positions


def reconstruct_from_tiles(tiles: np.ndarray, positions, shape, tile: int = 128):
    """Recompose une image (H,W) à partir des prédictions par tuile (vote moyen)."""
    H, W = shape
    acc = np.zeros((H, W), dtype=np.float32)
    cnt = np.zeros((H, W), dtype=np.float32)
    for t, (r0, c0) in zip(tiles, positions):
        acc[r0:r0 + tile, c0:c0 + tile] += t
        cnt[r0:r0 + tile, c0:c0 + tile] += 1
    return acc / np.maximum(cnt, 1)
