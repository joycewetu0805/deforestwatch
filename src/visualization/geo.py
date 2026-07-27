"""
Géoréférencement des grilles rasters pour les cartes interactives.

Les modèles travaillent sur des grilles de pixels sans coordonnées. Pour poser
ces sorties sur un vrai fond de carte, il faut deux choses : l'emprise
géographique de la zone d'étude, et une conversion des tableaux numpy vers un
format que deck.gl sait afficher.

Le format retenu est une liste de cellules carrées géolocalisées, et non une
image superposée. Trois raisons :

  - le rendu JSON de pydeck fait passer les chaînes par un parseur
    d'expressions, qui rejette aussi bien un data URI qu'un chemin relatif :
    une couche image n'est donc utilisable qu'avec une URL absolue servie par
    un serveur de fichiers ;
  - une cellule porte sa valeur, donc chaque point de la carte peut afficher
    une infobulle, ce qu'une image ne permet pas ;
  - le même tableau alimente le dashboard Streamlit et le frontend React, sans
    conversion intermédiaire.

La finesse est réglable par le pas `step` : c'est le compromis entre précision
visuelle et poids des données transmises au navigateur.
"""

from __future__ import annotations

import math

import numpy as np

from config.settings import (
    CLASS_COLORS, LAND_COVER_CLASSES, PIXEL_AREA_HA, pixel_area_ha, settings,
)
from src.utils.helpers import bbox_from_center

# Rampe de risque : sable, ocre, rouge sombre (mêmes teintes que les figures du PDF)
RISK_RAMP = [
    (0.00, (247, 244, 234)),
    (0.35, (243, 217, 164)),
    (0.60, (232, 163, 61)),
    (0.80, (209, 96, 28)),
    (1.00, (161, 29, 29)),
]

FOREST_KEPT_COLOR = [11, 110, 45]
FOREST_LOST_COLOR = [161, 29, 29]

# Hauteur d'une colonne à 100/100 de risque, en mètres.
MAX_COLUMN_HEIGHT_M = 6000.0


# ──────────────────────────────────────────────────────────────────────────
# Emprise
# ──────────────────────────────────────────────────────────────────────────
def bounds() -> dict:
    """Emprise de la zone d'étude : {west, south, east, north} en degrés."""
    b = bbox_from_center(settings.study_area_lat, settings.study_area_lon,
                         settings.study_area_buffer_km)
    # float() explicite : bbox_from_center renvoie des np.float64, que le module
    # json refuse de sérialiser pour l'export du frontend.
    return {
        "west": float(b["min_lon"]), "south": float(b["min_lat"]),
        "east": float(b["max_lon"]), "north": float(b["max_lat"]),
    }


def center() -> tuple[float, float]:
    """Centre de la zone d'étude : (latitude, longitude)."""
    return settings.study_area_lat, settings.study_area_lon


def pixel_to_lonlat(row: float, col: float, shape: tuple[int, int]) -> tuple[float, float]:
    """Centre géographique du pixel (row, col). La ligne 0 est au nord."""
    h, w = shape
    b = bounds()
    lon = b["west"] + (col + 0.5) / w * (b["east"] - b["west"])
    lat = b["north"] - (row + 0.5) / h * (b["north"] - b["south"])
    return lon, lat


def cell_radius_m(shape: tuple[int, int], step: int) -> float:
    """
    Rayon à donner au ColumnLayer pour que les cellules carrées pavent la zone.

    deck.gl dessine un polygone régulier inscrit dans un cercle de ce rayon.
    Avec 4 côtés, le rayon est donc la demi-diagonale du carré, et non le
    demi-côté, sinon les cellules laissent des interstices.
    """
    n_cols = max(shape[1] // step, 1)
    side_m = settings.study_area_buffer_km * 2 * 1000 / n_cols
    return side_m / 2 * math.sqrt(2)


def cell_area_ha(step: int, shape: tuple[int, int] | None = None) -> float:
    """Surface au sol d'une cellule agrégée, en hectares.

    `shape` : dimensions de la grille source. Sans elle, la résolution par
    défaut est supposée, ce qui n'est juste que pour une grille GRID_SIZE.
    """
    unit = pixel_area_ha(shape) if shape is not None else PIXEL_AREA_HA
    return unit * step * step


# ──────────────────────────────────────────────────────────────────────────
# Couleurs
# ──────────────────────────────────────────────────────────────────────────
def _hex_to_rgb(value: str) -> list[int]:
    value = value.lstrip("#")
    return [int(value[i:i + 2], 16) for i in (0, 2, 4)]


def risk_color(value: float) -> list[int]:
    """Couleur RGB d'un score de risque 0..100, interpolée sur la rampe."""
    t = float(np.clip(value, 0, 100)) / 100.0
    for (t0, c0), (t1, c1) in zip(RISK_RAMP, RISK_RAMP[1:]):
        if t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return [int(round(c0[i] + f * (c1[i] - c0[i]))) for i in range(3)]
    return list(RISK_RAMP[-1][1])


# ──────────────────────────────────────────────────────────────────────────
# Agrégation des grilles
# ──────────────────────────────────────────────────────────────────────────
def _blocks(grid: np.ndarray, step: int) -> np.ndarray:
    """Découpe la grille en blocs step x step. Renvoie (n_rows, step, n_cols, step)."""
    h, w = grid.shape
    hh, ww = (h // step) * step, (w // step) * step
    return grid[:hh, :ww].reshape(hh // step, step, ww // step, step)


def _aggregate_max(grid: np.ndarray, step: int) -> np.ndarray:
    """Maximum par bloc. Sur une carte de risque, un point chaud isolé ne doit
    pas être lissé par une moyenne."""
    return _blocks(grid, step).max(axis=(1, 3))


def _aggregate_mode(grid: np.ndarray, step: int, n_classes: int) -> np.ndarray:
    """Classe majoritaire par bloc, pour les grilles catégorielles."""
    blocks = _blocks(grid, step)
    counts = np.stack([(blocks == c).sum(axis=(1, 3)) for c in range(n_classes)])
    return counts.argmax(axis=0)


def _grid_positions(shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    """Longitudes et latitudes des centres de cellules d'une grille agrégée."""
    n_rows, n_cols = shape
    b = bounds()
    lons = b["west"] + (np.arange(n_cols) + 0.5) / n_cols * (b["east"] - b["west"])
    lats = b["north"] - (np.arange(n_rows) + 0.5) / n_rows * (b["north"] - b["south"])
    return lons, lats


# ──────────────────────────────────────────────────────────────────────────
# Couches
# ──────────────────────────────────────────────────────────────────────────
def risk_cells(risk: np.ndarray, step: int = 3, min_risk: float = 5.0,
               max_height_m: float = MAX_COLUMN_HEIGHT_M) -> list[dict]:
    """
    Cellules de risque, prêtes pour un ColumnLayer.

    Chaque cellule porte sa hauteur en mètres et sa couleur, pour que la même
    donnée serve en 2D (hauteur ignorée) comme en 3D (colonnes extrudées).
    """
    agg = _aggregate_max(risk, step)
    lons, lats = _grid_positions(agg.shape)

    cells: list[dict] = []
    for r in range(agg.shape[0]):
        for c in range(agg.shape[1]):
            value = float(agg[r, c])
            if value < min_risk:
                continue
            # arrondi d'abord : la hauteur doit correspondre à la valeur
            # affichée dans l'infobulle, pas à la valeur brute.
            value = round(value, 1)
            cells.append({
                "lon": round(float(lons[c]), 5),
                "lat": round(float(lats[r]), 5),
                "value": value,
                "height": round(value / 100.0 * max_height_m, 1),
                "color": risk_color(value),
            })
    return cells


def landcover_cells(lc: np.ndarray, step: int = 3) -> list[dict]:
    """Cellules de couverture du sol, colorées par classe."""
    agg = _aggregate_mode(lc, step, len(LAND_COVER_CLASSES))
    lons, lats = _grid_positions(agg.shape)
    palette = {c: _hex_to_rgb(CLASS_COLORS[c]) for c in CLASS_COLORS}

    cells: list[dict] = []
    for r in range(agg.shape[0]):
        for c in range(agg.shape[1]):
            code = int(agg[r, c])
            cells.append({
                "lon": round(float(lons[c]), 5),
                "lat": round(float(lats[r]), 5),
                "value": code,
                "label": LAND_COVER_CLASSES[code],
                "height": 0.0,
                "color": palette[code],
            })
    return cells


def loss_cells(lc_start: np.ndarray, lc_end: np.ndarray, step: int = 3,
               max_height_m: float = 3000.0) -> list[dict]:
    """
    Cellules de perte forestière entre deux années.

    La hauteur encode la part de la cellule effectivement perdue, ce qui
    distingue une conversion totale d'un grignotage de lisière.
    """
    forest_start = (lc_start == 0) | (lc_start == 1)
    forest_end = (lc_end == 0) | (lc_end == 1)

    lost_ratio = _blocks((forest_start & ~forest_end).astype(np.float32), step).mean(axis=(1, 3))
    kept_ratio = _blocks((forest_start & forest_end).astype(np.float32), step).mean(axis=(1, 3))
    lons, lats = _grid_positions(lost_ratio.shape)
    cell_ha = cell_area_ha(step, lc_start.shape)

    cells: list[dict] = []
    for r in range(lost_ratio.shape[0]):
        for c in range(lost_ratio.shape[1]):
            lost, kept = float(lost_ratio[r, c]), float(kept_ratio[r, c])
            if lost < 0.02 and kept < 0.02:
                continue
            is_loss = lost >= kept
            ratio = lost if is_loss else kept
            cells.append({
                "lon": round(float(lons[c]), 5),
                "lat": round(float(lats[r]), 5),
                "value": round(lost * cell_ha, 1),
                "label": "Forêt perdue" if is_loss else "Forêt conservée",
                "height": round(lost * max_height_m, 1),
                "color": FOREST_LOST_COLOR if is_loss else FOREST_KEPT_COLOR,
                "opacity_hint": round(0.35 + 0.65 * ratio, 2),
            })
    return cells


# ──────────────────────────────────────────────────────────────────────────
# Points chauds et légendes
# ──────────────────────────────────────────────────────────────────────────
def hotspots(risk: np.ndarray, threshold: float = 80.0, limit: int = 12,
             step: int = 8) -> list[dict]:
    """Les cellules les plus à risque, géolocalisées, pour un tableau ou des marqueurs."""
    cells = risk_cells(risk, step=step, min_risk=threshold)
    cells.sort(key=lambda c: c["value"], reverse=True)
    area = cell_area_ha(step, risk.shape)
    for cell in cells[:limit]:
        cell["surface_ha"] = round(area, 1)
    return cells[:limit]


def legend() -> dict:
    """Légendes des couches, pour l'affichage dans les interfaces."""
    return {
        "landcover": [{"label": name, "color": CLASS_COLORS[code]}
                      for code, name in LAND_COVER_CLASSES.items()],
        "risk": [{"label": str(int(t * 100)), "color": "#%02x%02x%02x" % c}
                 for t, c in RISK_RAMP],
        "loss": [{"label": "Forêt conservée", "color": "#0b6e2d"},
                 {"label": "Forêt perdue", "color": "#a11d1d"}],
    }
