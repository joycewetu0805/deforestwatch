"""
Création de mosaïques temporelles médianes par année (saison sèche juin–sept).
Les images trop nuageuses (> 70 %) sont écartées avant la composition médiane.
"""

from __future__ import annotations

import numpy as np

from src.preprocessing.cloud_masking import valid_fraction
from src.utils.logger import get_logger

log = get_logger("mosaic")

MAX_CLOUD_PCT = 70.0


def median_composite(images: list[np.ndarray], masks: list[np.ndarray]) -> np.ndarray:
    """
    Compose une mosaïque médiane à partir d'une pile d'images (H,W,B) et de leurs
    masques de validité. Les pixels invalides sont ignorés (NaN -> nanmedian).
    """
    kept = []
    for img, mask in zip(images, masks):
        cloud_pct = 100.0 - valid_fraction(mask)
        if cloud_pct > MAX_CLOUD_PCT:
            log.warning(f"Image écartée : {cloud_pct:.1f}% de nuages (> {MAX_CLOUD_PCT}%).")
            continue
        masked = img.astype(np.float32).copy()
        masked[~mask] = np.nan
        kept.append(masked)

    if not kept:
        raise ValueError("Aucune image valide pour composer la mosaïque.")

    stack = np.stack(kept, axis=0)
    with np.errstate(all="ignore"):
        composite = np.nanmedian(stack, axis=0)
    # Comble les pixels restés NaN (jamais valides) par la médiane globale
    composite = np.where(np.isnan(composite), np.nanmedian(composite), composite)
    log.info(f"Mosaïque composée à partir de {len(kept)}/{len(images)} images.")
    return composite.astype(np.float32)
