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
from pathlib import Path

from config.settings import PROJECT_ROOT
from src.data import provider
from src.utils.logger import get_logger
from src.visualization import maps

log = get_logger("export_frontend_demo")

OUT = PROJECT_ROOT / "frontend" / "public" / "demo"


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

    log.info(f"Assets démo exportés dans {OUT} : "
             f"{len(series)} cartes + stats.json + risk.png")


if __name__ == "__main__":
    main()
