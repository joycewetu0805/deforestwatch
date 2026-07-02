"""
Détection d'alertes de déforestation.

Scanne la série temporelle de couverture du sol par secteurs (blocs de la grille)
et émet une alerte lorsqu'un secteur perd, d'une année à l'autre, plus de forêt
qu'un seuil donné. Chaque alerte est géolocalisée et classée par sévérité.

Fonctionne indifféremment sur les données de démonstration ou réelles (via le
provider), donc les alertes reflètent la source active.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict

import numpy as np

from config.settings import PIXEL_AREA_HA, settings
from src.data import provider

# Seuil de perte (hectares) par secteur et par an au-delà duquel on alerte
DEFAULT_THRESHOLD_HA = 400.0
N_BLOCKS = 8  # découpage de la zone en 8x8 = 64 secteurs

SEVERITIES = ("modérée", "élevée", "critique")


@dataclass
class Alert:
    id: str
    sector: str
    lat: float
    lon: float
    year: int
    area_lost_ha: float
    severity: str
    forest_before_ha: float
    forest_after_ha: float

    def to_dict(self) -> dict:
        return asdict(self)


def _severity(area_lost_ha: float, threshold: float) -> str:
    if area_lost_ha >= 3 * threshold:
        return "critique"
    if area_lost_ha >= 1.5 * threshold:
        return "élevée"
    return "modérée"


def _sector_center_latlon(bi: int, bj: int, n: int) -> tuple[float, float]:
    """Centre géographique d'un secteur (bi, bj) dans la zone d'étude."""
    from src.utils.helpers import bbox_from_center

    b = bbox_from_center(settings.study_area_lat, settings.study_area_lon,
                         settings.study_area_buffer_km)
    # bi = ligne (latitude, du haut=nord vers le bas=sud), bj = colonne (longitude)
    fy = (bi + 0.5) / n
    fx = (bj + 0.5) / n
    lat = b["max_lat"] - fy * (b["max_lat"] - b["min_lat"])
    lon = b["min_lon"] + fx * (b["max_lon"] - b["min_lon"])
    return round(lat, 4), round(lon, 4)


def detect_alerts(threshold_ha: float = DEFAULT_THRESHOLD_HA,
                  n_blocks: int = N_BLOCKS) -> list[Alert]:
    """Renvoie la liste des alertes détectées (triées : plus récentes/graves d'abord)."""
    series = provider.landcover_series()
    years = sorted(series.keys())
    if len(years) < 2:
        return []

    grid = series[years[0]].shape[0]
    block = max(grid // n_blocks, 1)
    alerts: list[Alert] = []

    def forest_ha(sub: np.ndarray) -> float:
        return float(np.sum((sub == 0) | (sub == 1))) * PIXEL_AREA_HA

    for k in range(1, len(years)):
        y_prev, y_cur = years[k - 1], years[k]
        lc_prev, lc_cur = series[y_prev], series[y_cur]
        for bi in range(n_blocks):
            for bj in range(n_blocks):
                r0, c0 = bi * block, bj * block
                sub_prev = lc_prev[r0:r0 + block, c0:c0 + block]
                sub_cur = lc_cur[r0:r0 + block, c0:c0 + block]
                before, after = forest_ha(sub_prev), forest_ha(sub_cur)
                lost = before - after
                if lost >= threshold_ha:
                    lat, lon = _sector_center_latlon(bi, bj, n_blocks)
                    aid = hashlib.md5(f"{bi}-{bj}-{y_cur}".encode()).hexdigest()[:8]
                    alerts.append(Alert(
                        id=aid, sector=f"S{bi}{bj}", lat=lat, lon=lon, year=y_cur,
                        area_lost_ha=round(lost, 1), severity=_severity(lost, threshold_ha),
                        forest_before_ha=round(before, 1), forest_after_ha=round(after, 1),
                    ))

    sev_rank = {s: i for i, s in enumerate(SEVERITIES)}
    alerts.sort(key=lambda a: (a.year, sev_rank[a.severity], a.area_lost_ha), reverse=True)
    return alerts


def active_alerts(threshold_ha: float = DEFAULT_THRESHOLD_HA) -> list[Alert]:
    """Alertes de la dernière transition annuelle (les plus récentes)."""
    alerts = detect_alerts(threshold_ha)
    if not alerts:
        return []
    last_year = max(a.year for a in alerts)
    return [a for a in alerts if a.year == last_year]


def summary(threshold_ha: float = DEFAULT_THRESHOLD_HA) -> dict:
    """Synthèse : nombre d'alertes par sévérité, surface totale, année la plus touchée."""
    alerts = detect_alerts(threshold_ha)
    by_sev = {s: 0 for s in SEVERITIES}
    for a in alerts:
        by_sev[a.severity] += 1
    total_lost = round(sum(a.area_lost_ha for a in alerts), 1)
    worst_year = None
    if alerts:
        per_year: dict[int, float] = {}
        for a in alerts:
            per_year[a.year] = per_year.get(a.year, 0) + a.area_lost_ha
        worst_year = max(per_year, key=per_year.get)
    return {
        "total_alerts": len(alerts),
        "by_severity": by_sev,
        "total_area_lost_ha": total_lost,
        "active_alerts": len(active_alerts(threshold_ha)),
        "worst_year": worst_year,
        "threshold_ha": threshold_ha,
    }


def main() -> None:
    from src.utils.logger import get_logger

    log = get_logger("alerts")
    s = summary()
    log.info(f"Alertes : {s}")
    for a in active_alerts()[:5]:
        log.info(f"  [{a.severity}] {a.sector} {a.year} — {a.area_lost_ha} ha "
                 f"({a.lat}, {a.lon})")


if __name__ == "__main__":
    main()
