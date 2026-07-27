"""
Exporte des assets de démonstration statiques pour le frontend React, afin que
la vitrine (et la « Machine à remonter le temps ») fonctionne en autonomie sur
un hébergement statique (Vercel) même sans backend FastAPI.

Génère dans frontend/public/demo/ :
  - stats.json                 statistiques annuelles
  - landcover/{year}.png       carte de couverture par année
  - risk.png                   carte de risque

Usage : python -m scripts.export_frontend_demo
"""

from __future__ import annotations

import io
import json

from config.settings import PROJECT_ROOT
from src.data import provider
from src.utils.logger import get_logger
from src.visualization import maps

log = get_logger("export_frontend_demo")

OUT = PROJECT_ROOT / "frontend" / "public" / "demo"

# Finesse des cellules 3D exportées vers le frontend. Compromis entre précision
# et poids du fichier : le site est statique, tout est téléchargé d'un coup.
MAP_STEP = 4


def _png(rgb, size: int = 512) -> bytes:
    from PIL import Image

    img = Image.fromarray(rgb).resize((size, size), Image.NEAREST)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    lc_dir = OUT / "landcover"
    lc_dir.mkdir(parents=True, exist_ok=True)

    stats = provider.yearly_statistics()
    (OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False), encoding="utf-8")

    series = provider.landcover_series()
    for year, lc in series.items():
        (lc_dir / f"{year}.png").write_bytes(_png(maps.classification_to_rgb(lc)))
    (OUT / "risk.png").write_bytes(_png(maps.risk_to_rgb(provider.risk_map())))

    # Alertes de déforestation (pour le panneau du frontend, mode statique)
    from src.analysis import alerts as alerts_engine

    active = [a.to_dict() for a in alerts_engine.active_alerts()]
    (OUT / "alerts.json").write_text(json.dumps(active, ensure_ascii=False), encoding="utf-8")
    (OUT / "alerts_summary.json").write_text(
        json.dumps(alerts_engine.summary(), ensure_ascii=False), encoding="utf-8")

    # Impact : carbone + atout radar (pour le panneau du frontend en mode statique)
    from src.analysis import carbon as carbon_engine
    from src.data.radar import cloud_penetration_demo
    from config.settings import ANALYSIS_YEARS

    impact = {"carbon": carbon_engine.summary(),
              "radar": cloud_penetration_demo(ANALYSIS_YEARS[-1])}
    (OUT / "impact.json").write_text(json.dumps(impact, ensure_ascii=False), encoding="utf-8")

    # Carte interactive : emprise géographique, cellules 3D de risque, légendes.
    # Les couches 2D réutilisent les PNG déjà exportés ci-dessus, posés sur le
    # fond de carte par leur emprise.
    from src.visualization import geo

    risk = provider.risk_map()
    years = sorted(series)
    map_payload = {
        "bounds": geo.bounds(),
        "center": {"lat": geo.center()[0], "lon": geo.center()[1]},
        "years": years,
        "legend": geo.legend(),
        "cell": {"step": MAP_STEP,
                 "radius_m": round(geo.cell_radius_m(risk.shape, MAP_STEP), 1),
                 "surface_ha": round(geo.cell_area_ha(MAP_STEP), 1)},
        "risk_cells": geo.risk_cells(risk, step=MAP_STEP),
        "loss_cells": geo.loss_cells(series[years[0]], series[years[-1]], step=MAP_STEP),
    }
    (OUT / "map.json").write_text(json.dumps(map_payload, ensure_ascii=False),
                                  encoding="utf-8")

    log.info(f"Assets démo exportés dans {OUT} : {len(series)} cartes + stats.json "
             f"+ risk.png + {len(active)} alertes + impact.json + map.json "
             f"({len(map_payload['risk_cells'])} cellules de risque)")


if __name__ == "__main__":
    main()
