"""Cartes interactives Folium et rendus matriciels colorés des classifications."""

from __future__ import annotations

import numpy as np

from config.settings import CLASS_COLORS, NUM_CLASSES, settings


def classification_to_rgb(lc: np.ndarray) -> np.ndarray:
    """Convertit une carte de classes (H,W) en image RGB (H,W,3) uint8."""
    rgb = np.zeros((*lc.shape, 3), dtype=np.uint8)
    for c in range(NUM_CLASSES):
        color = CLASS_COLORS[c].lstrip("#")
        r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
        mask = lc == c
        rgb[mask] = [r, g, b]
    return rgb


def risk_to_rgb(risk: np.ndarray) -> np.ndarray:
    """Carte de risque 0–100 → dégradé vert→jaune→rouge."""
    r = np.clip(risk / 100, 0, 1)
    rgb = np.zeros((*risk.shape, 3), dtype=np.uint8)
    # vert (bas) -> jaune (milieu) -> rouge (haut)
    rgb[..., 0] = np.clip(r * 2, 0, 1) * 255          # rouge croît
    rgb[..., 1] = np.clip((1 - r) * 2, 0, 1) * 255    # vert décroît
    return rgb


def study_area_map(zoom: int = 9):
    """Carte Folium centrée sur la zone d'étude."""
    import folium

    m = folium.Map(
        location=[settings.study_area_lat, settings.study_area_lon],
        zoom_start=zoom, tiles="CartoDB dark_matter",
    )
    folium.Marker(
        [settings.study_area_lat, settings.study_area_lon],
        popup="Inongo — Mai-Ndombe", icon=folium.Icon(color="green", icon="leaf"),
    ).add_to(m)
    from src.utils.helpers import bbox_from_center

    bbox = bbox_from_center(settings.study_area_lat, settings.study_area_lon,
                            settings.study_area_buffer_km)
    folium.Rectangle(
        bounds=[[bbox["min_lat"], bbox["min_lon"]], [bbox["max_lat"], bbox["max_lon"]]],
        color="#10B981", fill=True, fill_opacity=0.1, popup="Zone d'étude ~50×50 km",
    ).add_to(m)
    return m
