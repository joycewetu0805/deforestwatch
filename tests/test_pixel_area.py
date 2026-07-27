"""
Tests de la conversion pixels vers hectares.

Le piège : la constante PIXEL_AREA_HA est calculée pour une grille
GRID_SIZE x GRID_SIZE. Une image réelle exportée depuis Google Earth Engine
n'a aucune raison de faire cette taille, et toute surface calculée avec la
mauvaise résolution est fausse dans le rapport du carré des dimensions.
"""

from __future__ import annotations

import numpy as np
import pytest

from config.settings import (
    GRID_SIZE, PIXEL_AREA_HA, STUDY_AREA_SIDE_M, pixel_area_ha,
)
from src.utils import synthetic

ZONE_HA = (STUDY_AREA_SIDE_M ** 2) / 10_000


def test_constante_coherente_avec_la_grille_par_defaut():
    assert pixel_area_ha((GRID_SIZE, GRID_SIZE)) == pytest.approx(PIXEL_AREA_HA)


@pytest.mark.parametrize("cote", [128, 256, 400, 1024, 5000])
def test_la_somme_des_pixels_couvre_la_zone(cote):
    """Quelle que soit la résolution, tous les pixels réunis font la zone d'étude."""
    total = pixel_area_ha((cote, cote)) * cote * cote
    assert total == pytest.approx(ZONE_HA, rel=1e-9)


def test_resolution_sentinel2_a_dix_metres():
    """5000 pixels sur 50 km, soit 10 m par pixel, donc 0,01 ha."""
    assert pixel_area_ha((5000, 5000)) == pytest.approx(0.01, rel=1e-9)


def test_surface_inversement_proportionnelle_au_carre():
    """Doubler la résolution divise la surface d'un pixel par quatre."""
    assert pixel_area_ha((256, 256)) == pytest.approx(4 * pixel_area_ha((512, 512)))


def test_grille_non_carree():
    aire = pixel_area_ha((200, 400))
    assert aire * 200 * 400 == pytest.approx(ZONE_HA, rel=1e-9)


@pytest.mark.parametrize("cote", [128, 400])
def test_statistiques_annuelles_suivent_la_resolution(cote):
    """
    Le total forestier ne doit pas dépendre de la résolution de l'image.

    Deux grilles différentes décrivent la même forêt : les hectares annoncés
    doivent concorder, à la précision d'échantillonnage près.
    """
    serie = synthetic.generate_landcover_series(grid=cote)
    stats = synthetic.yearly_statistics(series=serie)
    lc = serie[max(serie)]
    part_foret = float(np.mean((lc == 0) | (lc == 1)))
    assert stats[-1]["total_forest_ha"] == pytest.approx(part_foret * ZONE_HA, rel=1e-3)


def test_deux_resolutions_donnent_le_meme_ordre_de_grandeur():
    petite = synthetic.yearly_statistics(
        series=synthetic.generate_landcover_series(grid=128))[-1]["total_forest_ha"]
    grande = synthetic.yearly_statistics(
        series=synthetic.generate_landcover_series(grid=512))[-1]["total_forest_ha"]
    assert petite == pytest.approx(grande, rel=0.05), \
        "changer la résolution ne doit pas changer la surface annoncée"


def test_env_file_est_un_chemin_absolu():
    """
    Le .env doit être résolu depuis la racine du projet, pas depuis le
    répertoire courant. Sinon un dashboard lancé ailleurs retombe
    silencieusement en mode démonstration malgré DEMO_MODE=false.
    """
    from pathlib import Path

    from config.settings import PROJECT_ROOT, Settings

    chemin = Path(Settings.Config.env_file)
    assert chemin.is_absolute()
    assert chemin == PROJECT_ROOT / ".env"
