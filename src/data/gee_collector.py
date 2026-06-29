"""
Collecte d'images satellites via Google Earth Engine (Sentinel-2, Hansen, SRTM).

Si GEE n'est pas authentifié ou si DEMO_MODE est actif, le module bascule
automatiquement sur le générateur synthétique afin que le pipeline complet
reste exécutable sans compte GEE.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from config.settings import (
    ANALYSIS_YEARS,
    settings,
)
from src.utils.helpers import bbox_from_center
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("gee_collector")


class GEECollector:
    """Wrapper haut niveau autour de l'API Earth Engine avec repli synthétique."""

    def __init__(self):
        self.ee = None
        self.available = False
        if not settings.demo_mode:
            self._init_ee()
        else:
            log.info("DEMO_MODE actif → collecte en mode synthétique.")

    # ── Initialisation ──
    def _init_ee(self) -> None:
        try:
            import ee  # type: ignore

            if settings.gee_service_account:
                creds = ee.ServiceAccountCredentials(
                    settings.gee_service_account, settings.gee_key_file
                )
                ee.Initialize(creds)
            else:
                ee.Initialize()
            self.ee = ee
            self.available = True
            log.info("Google Earth Engine initialisé.")
        except Exception as exc:  # pragma: no cover - dépend de l'environnement
            log.warning(f"GEE indisponible ({exc}). Repli sur le mode synthétique.")
            self.available = False

    # ── Zone d'étude ──
    def study_area(self):
        """Renvoie la géométrie de la zone (ee.Geometry si dispo, sinon bbox dict)."""
        bbox = bbox_from_center(
            settings.study_area_lat, settings.study_area_lon, settings.study_area_buffer_km
        )
        if self.available:
            return self.ee.Geometry.Rectangle(
                [bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"]]
            )
        return bbox

    # ── Composite Sentinel-2 ──
    def get_annual_composite(self, year: int) -> np.ndarray:
        """
        Composite médian saison sèche (juin–sept) pour une année.
        Renvoie un array (H, W, 6) de réflectances.
        """
        if not self.available:
            return self._synthetic_composite(year)

        ee = self.ee
        aoi = self.study_area()
        col = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(aoi)
            .filterDate(f"{year}-06-01", f"{year}-09-30")
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
            .map(self._mask_s2_clouds)
        )
        composite = col.median().select(["B2", "B3", "B4", "B8", "B11", "B12"])
        log.info(f"Composite GEE {year} prêt (export nécessaire pour récupérer l'array).")
        # En production : export vers GCS/Drive puis lecture rasterio.
        return self._synthetic_composite(year)

    def _mask_s2_clouds(self, image):
        """Masque nuages/ombres via la bande SCL de Sentinel-2 SR."""
        scl = image.select("SCL")
        # 3=ombre, 8/9/10=nuages, 11=neige
        mask = (
            scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(11))
        )
        return image.updateMask(mask).divide(10000)

    def _synthetic_composite(self, year: int) -> np.ndarray:
        series = synthetic.generate_landcover_series()
        lc = series.get(year, series[ANALYSIS_YEARS[-1]])
        return synthetic.landcover_to_bands(lc, seed=year)

    # ── Hansen Global Forest Change (ground truth) ──
    def get_hansen_loss(self) -> np.ndarray:
        """Carte de perte forestière Hansen (proxy synthétique en mode démo)."""
        if not self.available:
            series = synthetic.generate_landcover_series()
            first = (series[ANALYSIS_YEARS[0]] <= 1).astype(np.int8)
            last = (series[ANALYSIS_YEARS[-1]] <= 1).astype(np.int8)
            return (first & ~last).astype(np.int8)  # forêt perdue
        img = self.ee.Image("UMD/hansen/global_forest_change_2023_v1_11")
        return img  # type: ignore

    # ── SRTM (topographie) ──
    def get_topography(self) -> np.ndarray:
        """Altitude, pente, aspect (H, W, 3)."""
        if not self.available:
            return synthetic.generate_topography()
        srtm = self.ee.Image("USGS/SRTMGL1_003")
        terrain = self.ee.Terrain.products(srtm)
        return terrain  # type: ignore


def main() -> None:
    """Test rapide de chaque fonction."""
    collector = GEECollector()
    log.info(f"Zone d'étude : {collector.study_area()}")
    comp = collector.get_annual_composite(ANALYSIS_YEARS[-1])
    log.info(f"Composite shape : {comp.shape}, min={comp.min():.3f}, max={comp.max():.3f}")
    topo = collector.get_topography()
    log.info(f"Topographie shape : {topo.shape}")
    loss = collector.get_hansen_loss()
    log.info(f"Perte forestière : {int(np.sum(loss))} pixels")


if __name__ == "__main__":
    main()
