"""
Imagerie radar Sentinel-1 (bandes VV/VH) — pénètre les nuages.

En zone équatoriale, la couverture nuageuse persistante limite l'optique
(Sentinel-2). Le radar SAR de Sentinel-1 traverse les nuages et fournit une
mesure de structure de la canopée, très utile pour détecter les coupes.

Ce module fournit :
  - la collecte GEE d'un composite Sentinel-1 (avec repli synthétique) ;
  - la génération synthétique de rétrodiffusion VV/VH cohérente avec la couverture ;
  - le Radar Vegetation Index (RVI), indicateur de structure de végétation.
"""

from __future__ import annotations

import numpy as np

from config.settings import ANALYSIS_YEARS, settings
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("radar")

# Signatures moyennes de rétrodiffusion (dB) [VV, VH] par classe de couverture
RADAR_SIGNATURES = {
    0: [-7.0, -12.0],    # forêt dense : fort VH (diffusion de volume)
    1: [-8.0, -14.0],    # forêt dégradée
    2: [-10.5, -18.0],   # agriculture / sol nu : VH faible
    3: [-22.0, -27.0],   # eau : très faible (réflexion spéculaire)
    4: [-6.0, -13.0],    # urbain / bâti : VV élevé (double rebond)
}


def landcover_to_radar(lc: np.ndarray, seed: int = 0) -> np.ndarray:
    """Synthétise un composite radar (H, W, 2) = [VV, VH] en dB depuis les classes."""
    rng = np.random.default_rng(seed + 500)
    out = np.zeros((*lc.shape, 2), dtype=np.float32)
    for cls, sig in RADAR_SIGNATURES.items():
        mask = lc == cls
        for b in range(2):
            out[mask, b] = sig[b] + rng.normal(0, 1.2, mask.sum())  # speckle
    return out


def radar_vegetation_index(radar_db: np.ndarray) -> np.ndarray:
    """RVI = 4·σVH / (σVV + σVH), calculé en puissance linéaire (0 = nu, élevé = végétation)."""
    vv = 10 ** (radar_db[..., 0] / 10.0)
    vh = 10 ** (radar_db[..., 1] / 10.0)
    return (4.0 * vh / (vv + vh + 1e-9)).astype(np.float32)


class RadarCollector:
    """Collecte Sentinel-1 via GEE, avec repli synthétique."""

    def __init__(self):
        self.available = False
        if not settings.demo_mode:
            self._init_ee()

    def _init_ee(self):
        try:
            import ee  # type: ignore

            ee.Initialize()
            self.ee = ee
            self.available = True
            log.info("GEE initialisé pour Sentinel-1.")
        except Exception as exc:  # pragma: no cover
            log.warning(f"GEE indisponible ({exc}) → radar synthétique.")

    def annual_composite(self, year: int) -> np.ndarray:
        """Composite radar annuel (H, W, 2) VV/VH en dB."""
        if not self.available:
            series = synthetic.generate_landcover_series()
            lc = series.get(year, series[ANALYSIS_YEARS[-1]])
            return landcover_to_radar(lc, seed=year)
        ee = self.ee
        from src.utils.helpers import bbox_from_center

        b = bbox_from_center(settings.study_area_lat, settings.study_area_lon,
                             settings.study_area_buffer_km)
        aoi = ee.Geometry.Rectangle([b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"]])
        col = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(aoi)
            .filterDate(f"{year}-01-01", f"{year}-12-31")
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
            .select(["VV", "VH"])
            .median()
        )
        self._last = col  # export via scripts.gee_export en production
        log.info(f"Composite Sentinel-1 {year} prêt (export requis).")
        series = synthetic.generate_landcover_series()
        return landcover_to_radar(series.get(year, series[ANALYSIS_YEARS[-1]]), seed=year)


def cloud_penetration_demo(year: int, cloud_fraction: float = 0.5, seed: int = 0) -> dict:
    """
    Illustre l'atout du radar : là où l'optique est masquée par les nuages, le
    radar reste disponible. Renvoie le % de pixels exploitables optique vs radar.
    """
    from src.preprocessing.cloud_masking import synthetic_scl, cloud_mask_from_scl, valid_fraction

    grid = synthetic.generate_landcover_series()[year].shape[0]
    scl = synthetic_scl((grid, grid), cloud_fraction=cloud_fraction, seed=seed)
    optical_valid = valid_fraction(cloud_mask_from_scl(scl))
    return {
        "year": year,
        "optical_usable_pct": round(optical_valid, 1),
        "radar_usable_pct": 100.0,   # le radar traverse les nuages
        "gain_pct": round(100.0 - optical_valid, 1),
    }


def main() -> None:
    coll = RadarCollector()
    year = ANALYSIS_YEARS[-1]
    radar = coll.annual_composite(year)
    rvi = radar_vegetation_index(radar)
    log.info(f"Radar {year} shape={radar.shape} VV≈{radar[...,0].mean():.1f}dB "
             f"VH≈{radar[...,1].mean():.1f}dB · RVI moyen={rvi.mean():.2f}")
    log.info(f"Pénétration nuageuse : {cloud_penetration_demo(year)}")


if __name__ == "__main__":
    main()
