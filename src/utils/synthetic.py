"""
Générateur de données synthétiques réalistes pour DeforestWatch-DRC.

En mode démo (settings.demo_mode), tout le pipeline — collecte, prétraitement,
modélisation, dashboard — fonctionne sans Google Earth Engine ni clés API.
Les données simulées reproduisent la dynamique de déforestation observée au
Mai-Ndombe : avancée d'un front agricole depuis les villages et les routes.
"""

from __future__ import annotations

import numpy as np

from config.settings import (
    ANALYSIS_YEARS,
    BAND_ORDER,
    GRID_SIZE,
    INDEX_ORDER,
    NUM_CLASSES,
    PIXEL_AREA_HA,
)


def _rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def generate_landcover_series(grid: int = GRID_SIZE, seed: int = 42) -> dict[int, np.ndarray]:
    """
    Génère une carte de couverture du sol (classes 0..4) pour chaque année.

    La forêt (classe 0) recule progressivement au profit de l'agriculture
    (classe 2) le long de fronts partant de "villages" et "routes".
    """
    rng = _rng(seed)
    yy, xx = np.mgrid[0:grid, 0:grid]

    # Réseau hydrographique (classe 3 = eau) : une rivière sinueuse
    river = np.abs(yy - (grid * 0.6 + 18 * np.sin(xx / 30.0))) < 3
    # Zone urbaine (classe 4) : la ville d'Inongo
    town_cx, town_cy = int(grid * 0.30), int(grid * 0.62)
    town = (xx - town_cx) ** 2 + (yy - town_cy) ** 2 < (grid * 0.04) ** 2

    # Sources de pression (villages + route)
    sources = [(int(grid * 0.30), int(grid * 0.62)),
               (int(grid * 0.70), int(grid * 0.35)),
               (int(grid * 0.50), int(grid * 0.80))]
    road = np.abs(xx - yy) < 4  # route diagonale

    # Distance aux sources de pression (sert de moteur de déforestation)
    dist = np.full((grid, grid), np.inf)
    for sx, sy in sources:
        d = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        dist = np.minimum(dist, d)
    dist = np.minimum(dist, np.where(road, 5.0, np.inf))
    dist_norm = dist / dist.max()

    series: dict[int, np.ndarray] = {}
    for i, year in enumerate(ANALYSIS_YEARS):
        progress = i / (len(ANALYSIS_YEARS) - 1)  # 0 -> 1
        lc = np.zeros((grid, grid), dtype=np.int8)  # tout forêt au départ

        # Seuil de déforestation qui s'étend avec le temps + bruit
        threshold = 0.10 + 0.45 * progress
        noise = rng.normal(0, 0.05, (grid, grid))
        deforested = (dist_norm + noise) < threshold

        # Forêt dégradée = frange autour des zones déforestées
        degraded = (dist_norm + noise < threshold + 0.08) & ~deforested

        lc[degraded] = 1
        lc[deforested] = 2
        lc[river] = 3
        lc[town] = 4
        series[year] = lc

    return series


def landcover_to_bands(lc: np.ndarray, seed: int = 0) -> np.ndarray:
    """
    Synthétise les 6 réflectances Sentinel-2 (B2,B3,B4,B8,B11,B12) à partir
    d'une carte de classes. Valeurs en réflectance 0..1.
    Renvoie un array (H, W, 6).
    """
    rng = _rng(seed + 100)
    h, w = lc.shape
    bands = np.zeros((h, w, 6), dtype=np.float32)

    # Signatures spectrales moyennes par classe [B2,B3,B4,B8,B11,B12]
    sig = {
        0: [0.03, 0.05, 0.03, 0.45, 0.18, 0.09],  # forêt dense : fort NIR
        1: [0.04, 0.07, 0.05, 0.38, 0.22, 0.13],  # forêt dégradée
        2: [0.10, 0.13, 0.16, 0.28, 0.34, 0.30],  # sol nu / agriculture
        3: [0.06, 0.08, 0.05, 0.02, 0.01, 0.01],  # eau : NIR très bas
        4: [0.14, 0.15, 0.17, 0.20, 0.28, 0.26],  # urbain
    }
    for cls, s in sig.items():
        mask = lc == cls
        for b in range(6):
            # bruit spectral marqué => classes partiellement chevauchantes
            # (rend la comparaison de modèles réaliste, métriques ~0.80-0.92)
            bands[mask, b] = s[b] + rng.normal(0, 0.045, mask.sum())
    return np.clip(bands, 0, 1)


def compute_indices_array(bands: np.ndarray) -> np.ndarray:
    """Calcule NDVI, EVI, NDWI, NBR depuis un array de bandes (H,W,6). -> (H,W,4)."""
    B2, B3, B4, B8, B11, B12 = [bands[..., i] for i in range(6)]
    eps = 1e-6
    ndvi = (B8 - B4) / (B8 + B4 + eps)
    evi = 2.5 * (B8 - B4) / (B8 + 6 * B4 - 7.5 * B2 + 1 + eps)
    ndwi = (B3 - B8) / (B3 + B8 + eps)
    nbr = (B8 - B12) / (B8 + B12 + eps)
    return np.stack([ndvi, evi, ndwi, nbr], axis=-1).astype(np.float32)


def generate_topography(grid: int = GRID_SIZE, seed: int = 7) -> np.ndarray:
    """Génère altitude, pente, aspect (H,W,3) — relief doux typique du bassin."""
    rng = _rng(seed)
    yy, xx = np.mgrid[0:grid, 0:grid] / grid
    altitude = 300 + 120 * (xx + 0.5 * yy) + rng.normal(0, 8, (grid, grid))
    gy, gx = np.gradient(altitude)
    slope = np.sqrt(gx ** 2 + gy ** 2)
    aspect = (np.degrees(np.arctan2(gy, gx)) + 360) % 360
    return np.stack([altitude, slope, aspect], axis=-1).astype(np.float32)


def build_pixel_dataset(seed: int = 42) -> dict:
    """
    Construit un dataset pixel-based (features 13-D + label) pour RF/XGBoost,
    en échantillonnant la dernière année disponible.
    Renvoie {X, y, feature_names}.
    """
    from config.settings import FEATURE_NAMES

    series = generate_landcover_series(seed=seed)
    year = ANALYSIS_YEARS[-1]
    lc = series[year]
    bands = landcover_to_bands(lc, seed=year)
    idx = compute_indices_array(bands)
    topo = generate_topography(seed=seed)

    features = np.concatenate([bands, idx, topo], axis=-1)  # (H,W,13)
    X = features.reshape(-1, features.shape[-1])
    y = lc.reshape(-1)
    return {"X": X, "y": y, "feature_names": FEATURE_NAMES}


def build_tile_dataset(n_tiles: int = 64, tile: int = 128, seed: int = 42) -> dict:
    """
    Construit un dataset tile-based (128x128x6) + masques pour le U-Net.
    Renvoie {X, y} avec X (N,128,128,6) et y (N,128,128).
    """
    rng = _rng(seed)
    series = generate_landcover_series(grid=max(GRID_SIZE, tile * 2), seed=seed)
    year = ANALYSIS_YEARS[-1]
    lc_full = series[year]
    bands_full = landcover_to_bands(lc_full, seed=year)
    H, W = lc_full.shape

    X, y = [], []
    for _ in range(n_tiles):
        r = rng.integers(0, H - tile)
        c = rng.integers(0, W - tile)
        X.append(bands_full[r:r + tile, c:c + tile, :])
        y.append(lc_full[r:r + tile, c:c + tile])
    return {"X": np.array(X, dtype=np.float32), "y": np.array(y, dtype=np.int8)}


def yearly_statistics(seed: int = 42) -> list[dict]:
    """Statistiques de déforestation année par année (pour API/dashboard)."""
    series = generate_landcover_series(seed=seed)
    stats = []
    prev_forest = None
    for year in ANALYSIS_YEARS:
        lc = series[year]
        forest_px = int(np.sum((lc == 0) | (lc == 1)))
        forest_ha = round(forest_px * PIXEL_AREA_HA, 1)
        loss_ha = round((prev_forest - forest_ha), 1) if prev_forest is not None else 0.0
        rate = round(100 * loss_ha / prev_forest, 2) if prev_forest else 0.0
        stats.append({
            "year": year,
            "total_forest_ha": forest_ha,
            "forest_loss_ha": max(loss_ha, 0.0),
            "deforestation_rate": max(rate, 0.0),
        })
        prev_forest = forest_ha
    return stats


def risk_map(seed: int = 42) -> np.ndarray:
    """Carte de risque 0..100 (probabilité de déforestation future par pixel)."""
    series = generate_landcover_series(seed=seed)
    last = series[ANALYSIS_YEARS[-1]]
    forest = (last == 0) | (last == 1)
    deforested = ~forest

    # Distance approx. de chaque pixel forêt à la déforestation la plus proche,
    # via dilatations successives (évite une dépendance à scipy).
    dist = np.full(forest.shape, np.inf, dtype=np.float32)
    frontier = deforested.copy()
    reached = deforested.copy()
    step = 0
    while not reached.all() and step < 40:
        dist[frontier & np.isinf(dist)] = step
        # dilatation 4-connexe
        grown = reached.copy()
        grown[1:, :] |= reached[:-1, :]
        grown[:-1, :] |= reached[1:, :]
        grown[:, 1:] |= reached[:, :-1]
        grown[:, :-1] |= reached[:, 1:]
        frontier = grown & ~reached
        reached = grown
        step += 1
    dist[np.isinf(dist)] = step

    risk = np.clip(100 * np.exp(-dist / 12.0), 0, 100)
    risk[~forest] = 0
    return risk.astype(np.float32)
