"""Tests du géoréférencement des grilles pour les cartes interactives."""

from __future__ import annotations

import json

import numpy as np
import pytest

from config.settings import LAND_COVER_CLASSES, settings
from src.utils import synthetic
from src.visualization import geo


@pytest.fixture(scope="module")
def series():
    return synthetic.generate_landcover_series()


@pytest.fixture(scope="module")
def risk(series):
    return synthetic.risk_map(series=series)


def test_bounds_encadrent_le_centre():
    b = geo.bounds()
    assert b["west"] < settings.study_area_lon < b["east"]
    assert b["south"] < settings.study_area_lat < b["north"]


def test_bounds_sont_serialisables_en_json():
    """L'export du frontend passe par json.dumps : pas de np.float64 toléré."""
    json.dumps(geo.bounds())


def test_ligne_zero_est_au_nord():
    shape = (256, 256)
    _, lat_haut = geo.pixel_to_lonlat(0, 0, shape)
    _, lat_bas = geo.pixel_to_lonlat(255, 0, shape)
    assert lat_haut > lat_bas


def test_colonne_zero_est_a_l_ouest():
    shape = (256, 256)
    lon_gauche, _ = geo.pixel_to_lonlat(0, 0, shape)
    lon_droite, _ = geo.pixel_to_lonlat(0, 255, shape)
    assert lon_gauche < lon_droite


def test_rayon_de_cellule_couvre_la_diagonale():
    """Le ColumnLayer inscrit le carré dans un cercle : le rayon doit être la
    demi-diagonale, sinon les cellules laissent des trous."""
    shape = (256, 256)
    step = 4
    rayon = geo.cell_radius_m(shape, step)
    cote = settings.study_area_buffer_km * 2 * 1000 / (shape[1] / step)
    assert rayon == pytest.approx(cote / 2 * np.sqrt(2), rel=1e-6)
    assert rayon > cote / 2


def test_risk_cells_filtre_le_seuil(risk):
    cells = geo.risk_cells(risk, step=4, min_risk=50)
    assert cells, "la zone d'étude doit contenir des cellules à risque"
    assert all(c["value"] >= 50 for c in cells)


def test_risk_cells_hauteur_proportionnelle(risk):
    cells = geo.risk_cells(risk, step=4, min_risk=1, max_height_m=1000)
    for cell in cells[:50]:
        assert cell["height"] == pytest.approx(cell["value"] / 100 * 1000, abs=0.1)


def test_risk_cells_serialisable(risk):
    json.dumps(geo.risk_cells(risk, step=8))


def test_landcover_cells_couvre_toute_la_grille(series):
    lc = series[max(series)]
    step = 4
    cells = geo.landcover_cells(lc, step=step)
    assert len(cells) == (lc.shape[0] // step) * (lc.shape[1] // step)
    assert all(c["value"] in LAND_COVER_CLASSES for c in cells)


def test_landcover_cells_prend_la_classe_majoritaire():
    """Un bloc homogène doit ressortir dans sa propre classe."""
    lc = np.full((8, 8), 3, dtype=np.int8)   # que de l'eau
    cells = geo.landcover_cells(lc, step=4)
    assert {c["value"] for c in cells} == {3}


def test_loss_cells_distingue_perte_et_conservation():
    depart = np.zeros((8, 8), dtype=np.int8)          # tout en forêt dense
    arrivee = depart.copy()
    arrivee[:4, :] = 2                                # moitié nord défrichée
    cells = geo.loss_cells(depart, arrivee, step=4)
    labels = {c["label"] for c in cells}
    assert labels == {"Forêt perdue", "Forêt conservée"}
    perdues = [c for c in cells if c["label"] == "Forêt perdue"]
    assert all(c["height"] > 0 for c in perdues)


def test_risk_color_suit_la_rampe():
    clair, sombre = geo.risk_color(0), geo.risk_color(100)
    assert sum(clair) > sum(sombre), "le risque élevé doit être plus sombre"
    assert all(0 <= v <= 255 for v in geo.risk_color(55))


def test_hotspots_tries_et_limites(risk):
    spots = geo.hotspots(risk, threshold=50, limit=5)
    assert len(spots) <= 5
    assert spots == sorted(spots, key=lambda s: s["value"], reverse=True)
    assert all("surface_ha" in s for s in spots)


def test_legende_couvre_les_trois_couches():
    legende = geo.legend()
    assert set(legende) == {"landcover", "risk", "loss"}
    assert len(legende["landcover"]) == len(LAND_COVER_CLASSES)
    assert all(i["color"].startswith("#") for i in legende["risk"])
