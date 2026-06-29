"""
Abstraction de source de données — forêt équatoriale du Bassin du Congo.

Permet de brancher de **vraies données** plus tard sans modifier le reste du code :

    - SyntheticSource : données simulées réalistes (mode démo, par défaut).
    - RasterSource    : vraies images GeoTIFF déposées dans data/raw/.

La source active est résolue automatiquement par `resolve_source()` :
  * si DEMO_MODE=false ET que des rasters réels existent dans data/raw/ → RasterSource
  * sinon → SyntheticSource

Toute la chaîne (datasets ML, statistiques, dashboard, API) consomme cette
interface via `src.data.provider`, donc déposer les vraies images suffit à
basculer l'ensemble de l'application sur les données réelles.

Format attendu pour les vraies données (voir data/raw/README.md) :
    data/raw/
      composites/{year}.tif     # 6 bandes Sentinel-2 : B2,B3,B4,B8,B11,B12 (réflectance)
      landcover/{year}.tif      # (optionnel) 1 bande, classes 0..4 (vérité terrain)
      topography.tif            # 3 bandes : altitude, pente, aspect
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from config.settings import ANALYSIS_YEARS, RAW_DIR, settings
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("sources")


class DataSource(ABC):
    """Interface commune à toutes les sources de données satellite."""

    name: str = "abstract"
    is_real: bool = False

    @abstractmethod
    def years(self) -> list[int]:
        """Années disponibles."""

    @abstractmethod
    def composite(self, year: int) -> np.ndarray:
        """Composite annuel (H, W, 6) — réflectances Sentinel-2."""

    @abstractmethod
    def landcover(self, year: int) -> np.ndarray | None:
        """Carte de classes (H, W) de vérité terrain, ou None si indisponible."""

    @abstractmethod
    def topography(self) -> np.ndarray:
        """Altitude, pente, aspect (H, W, 3)."""

    def landcover_series(self) -> dict[int, np.ndarray]:
        """Dictionnaire {année: carte de classes} pour les années étiquetées."""
        out = {}
        for y in self.years():
            lc = self.landcover(y)
            if lc is not None:
                out[y] = lc
        return out

    def has_labels(self) -> bool:
        return len(self.landcover_series()) > 0


# ──────────────────────────────────────────────────────────────────────────
# Source synthétique (mode démo)
# ──────────────────────────────────────────────────────────────────────────
class SyntheticSource(DataSource):
    name = "synthetic"
    is_real = False

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._series = synthetic.generate_landcover_series(seed=seed)
        self._topo = synthetic.generate_topography(seed=seed)

    def years(self) -> list[int]:
        return list(self._series.keys())

    def composite(self, year: int) -> np.ndarray:
        lc = self._series.get(year, self._series[max(self._series)])
        return synthetic.landcover_to_bands(lc, seed=year)

    def landcover(self, year: int) -> np.ndarray:
        return self._series.get(year, self._series[max(self._series)])

    def topography(self) -> np.ndarray:
        return self._topo


# ──────────────────────────────────────────────────────────────────────────
# Source réelle (GeoTIFF dans data/raw/)
# ──────────────────────────────────────────────────────────────────────────
class RasterSource(DataSource):
    name = "raster"
    is_real = True

    def __init__(self, root: Path = RAW_DIR):
        self.root = Path(root)
        self.composites_dir = self.root / "composites"
        self.landcover_dir = self.root / "landcover"
        self.topography_path = self.root / "topography.tif"

    # ── Détection ──
    @classmethod
    def has_data(cls, root: Path = RAW_DIR) -> bool:
        comp = Path(root) / "composites"
        return comp.is_dir() and any(comp.glob("*.tif"))

    def years(self) -> list[int]:
        if not self.composites_dir.is_dir():
            return []
        yrs = []
        for f in sorted(self.composites_dir.glob("*.tif")):
            try:
                yrs.append(int(f.stem))
            except ValueError:
                continue
        return yrs

    # ── Lecture raster ──
    def _read(self, path: Path) -> np.ndarray:
        """Lit un GeoTIFF en (H, W, bandes) via rasterio."""
        try:
            import rasterio
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "rasterio est requis pour lire les vraies données (pip install rasterio)."
            ) from exc
        with rasterio.open(path) as ds:
            arr = ds.read().astype(np.float32)  # (bandes, H, W)
        return np.transpose(arr, (1, 2, 0))      # (H, W, bandes)

    def composite(self, year: int) -> np.ndarray:
        path = self.composites_dir / f"{year}.tif"
        if not path.exists():
            raise FileNotFoundError(f"Composite réel introuvable : {path}")
        arr = self._read(path)
        if arr.shape[-1] < 6:
            raise ValueError(f"{path} : 6 bandes attendues, {arr.shape[-1]} trouvées.")
        return arr[..., :6]

    def landcover(self, year: int) -> np.ndarray | None:
        path = self.landcover_dir / f"{year}.tif"
        if not path.exists():
            return None
        return self._read(path)[..., 0].astype(np.int16)

    def topography(self) -> np.ndarray:
        if not self.topography_path.exists():
            # Repli : topographie synthétique à la taille du premier composite
            log.warning("topography.tif absent → topographie synthétique.")
            yrs = self.years()
            grid = self.composite(yrs[0]).shape[0] if yrs else 256
            return synthetic.generate_topography(grid=grid)
        return self._read(self.topography_path)[..., :3]


# ──────────────────────────────────────────────────────────────────────────
# Résolution de la source active
# ──────────────────────────────────────────────────────────────────────────
_cached_source: DataSource | None = None


def resolve_source(force: str | None = None, use_cache: bool = True) -> DataSource:
    """
    Renvoie la source de données active.

    force : 'synthetic' ou 'raster' pour imposer une source (sinon auto).
    """
    global _cached_source
    if use_cache and force is None and _cached_source is not None:
        return _cached_source

    if force == "raster":
        src: DataSource = RasterSource()
    elif force == "synthetic":
        src = SyntheticSource()
    elif not settings.demo_mode and RasterSource.has_data():
        src = RasterSource()
        log.info(f"Données réelles détectées dans {RAW_DIR} → source RasterSource "
                 f"({len(src.years())} années).")
    else:
        src = SyntheticSource()
        if not settings.demo_mode:
            log.warning("DEMO_MODE=false mais aucune donnée réelle trouvée dans "
                        f"{RAW_DIR}/composites/ → repli sur la source synthétique.")

    if force is None:
        _cached_source = src
    return src


def reset_cache() -> None:
    global _cached_source
    _cached_source = None


def describe_source() -> dict:
    """Métadonnées de la source active (pour l'API / le dashboard)."""
    src = resolve_source()
    return {
        "source": src.name,
        "is_real": src.is_real,
        "years": src.years(),
        "has_labels": src.has_labels(),
        "ecosystem": "Forêt tropicale humide équatoriale — Bassin du Congo (Mai-Ndombe)",
    }
