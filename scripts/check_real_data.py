"""
Vérifie le jeu de données réelles déposé dans data/raw/.

Contrôle : présence des composites, nombre de bandes, alignement des grilles,
disponibilité des étiquettes (entraînement supervisé) et de la topographie.

Usage : python -m scripts.check_real_data
"""

from __future__ import annotations

from config.settings import RAW_DIR
from src.data.sources import RasterSource
from src.utils.logger import get_logger

log = get_logger("check_real_data")


def main() -> None:
    if not RasterSource.has_data():
        log.warning(f"Aucun composite trouvé dans {RAW_DIR / 'composites'}. "
                    "L'application restera en mode démo (données synthétiques).")
        return

    src = RasterSource()
    years = src.years()
    log.info(f"Composites détectés : {years}")

    ref_shape = None
    ok = True
    for y in years:
        try:
            comp = src.composite(y)
        except Exception as exc:
            log.error(f"  {y} : ERREUR lecture composite — {exc}")
            ok = False
            continue
        if comp.shape[-1] < 6:
            log.error(f"  {y} : {comp.shape[-1]} bandes (6 attendues).")
            ok = False
        if ref_shape is None:
            ref_shape = comp.shape[:2]
        elif comp.shape[:2] != ref_shape:
            log.error(f"  {y} : grille {comp.shape[:2]} ≠ référence {ref_shape}.")
            ok = False
        else:
            log.info(f"  {y} : OK {comp.shape}")

    labels = src.landcover_series()
    if labels:
        log.info(f"Étiquettes (vérité terrain) disponibles pour : {sorted(labels)} "
                 "→ entraînement supervisé possible.")
    else:
        log.warning("Aucune carte landcover/ : statistiques et affichage possibles, "
                    "mais l'entraînement supervisé nécessite des étiquettes.")

    topo_ok = (RAW_DIR / "topography.tif").exists()
    log.info(f"topography.tif : {'présent' if topo_ok else 'absent (repli synthétique)'}")

    log.info("✅ Jeu de données valide." if ok else "❌ Problèmes détectés (voir ci-dessus).")


if __name__ == "__main__":
    main()
