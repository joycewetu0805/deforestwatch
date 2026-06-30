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

from config.settings import RAW_DIR, settings
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

# Override de mode à l'exécution (prioritaire sur la config .env) :
#   'demo' → toujours synthétique
#   'real' → données réelles si disponibles (sinon repli synthétique)
#   'auto' / None → résolution automatique selon DEMO_MODE + présence de data/raw
_forced_mode: str | None = None
MODES = ("auto", "demo", "real")


def set_mode(mode: str | None) -> str:
    """Force le mode de données à l'exécution et renvoie le mode effectif appliqué.

    Permet de basculer démo ↔ réel sans redémarrer ni éditer .env (utilisé par
    le toggle du dashboard). `mode` ∈ {'auto','demo','real',None}.
    """
    global _forced_mode
    if mode not in (None, *MODES):
        raise ValueError(f"Mode inconnu : {mode!r} (attendu : {MODES} ou None).")
    _forced_mode = None if mode in (None, "auto") else mode
    reset_cache()
    return current_mode()


def current_mode() -> str:
    """Mode demandé : 'demo', 'real' ou 'auto'."""
    if _forced_mode in ("demo", "real"):
        return _forced_mode
    return "auto"


def real_data_available() -> bool:
    """Vrai si de vraies images sont présentes dans data/raw/."""
    return RasterSource.has_data()


def resolve_source(force: str | None = None, use_cache: bool = True) -> DataSource:
    """
    Renvoie la source de données active.

    Priorité : `force` explicite > override `set_mode` > config .env (DEMO_MODE).
    force : 'synthetic' ou 'raster' pour imposer une source ponctuellement.
    """
    global _cached_source
    if use_cache and force is None and _cached_source is not None:
        return _cached_source

    # Mode effectif demandé
    if force == "raster":
        want_real = True
    elif force == "synthetic":
        want_real = False
    elif _forced_mode == "real":
        want_real = True
    elif _forced_mode == "demo":
        want_real = False
    else:  # auto : piloté par DEMO_MODE
        want_real = not settings.demo_mode

    if want_real and RasterSource.has_data():
        src: DataSource = RasterSource()
        log.info(f"Source = données réelles ({RAW_DIR}, {len(src.years())} années).")
    else:
        src = SyntheticSource()
        if want_real:
            log.warning("Mode 'réel' demandé mais aucune donnée dans "
                        f"{RAW_DIR}/composites/ → repli sur les données de démonstration.")

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
        "mode": current_mode(),
        "real_data_available": real_data_available(),
        "years": src.years(),
        "has_labels": src.has_labels(),
        "ecosystem": "Forêt tropicale humide équatoriale — Bassin du Congo (Mai-Ndombe)",
    }
