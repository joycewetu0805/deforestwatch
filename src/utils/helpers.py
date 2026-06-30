"""Fonctions utilitaires partagées."""

import json
from pathlib import Path
from typing import Any

import numpy as np


def ensure_dir(path: Path) -> Path:
    """Crée un dossier (et ses parents) s'il n'existe pas."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(obj: Any, path: Path) -> None:
    """Sauvegarde un objet en JSON (gère les types numpy)."""
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=_json_default)


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _json_default(o: Any):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Type non sérialisable : {type(o)}")


def km_to_degrees(km: float, lat: float) -> tuple[float, float]:
    """Convertit une distance en km en degrés (approx.) à une latitude donnée."""
    deg_lat = km / 111.0
    deg_lon = km / (111.320 * np.cos(np.radians(lat)) + 1e-9)
    return deg_lat, deg_lon


def bbox_from_center(lat: float, lon: float, buffer_km: float) -> dict:
    """Renvoie une bounding box {min_lat,max_lat,min_lon,max_lon} autour d'un centre."""
    dlat, dlon = km_to_degrees(buffer_km, lat)
    return {
        "min_lat": lat - dlat,
        "max_lat": lat + dlat,
        "min_lon": lon - dlon,
        "max_lon": lon + dlon,
    }
