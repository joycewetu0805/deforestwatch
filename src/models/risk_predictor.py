"""
Prédiction des zones à risque de déforestation future.

Modèle binaire (XGBoost / GradientBoosting) : "sera déforesté dans ~2 ans".
Features de risque par pixel : distance à la route, distance au village,
distance à la zone déjà déforestée, pente, altitude, taux de déforestation
historique du voisinage. Sortie : carte de risque 0–100.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from config.settings import MODELS_DIR
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("risk_predictor")

RISK_FEATURES = ["dist_road", "dist_village", "dist_deforested", "slope", "altitude", "neighbor_rate"]


def _risk_features(year_idx: int = -2, seed: int = 42):
    """Construit les features de risque + label (déforesté à l'année suivante)."""
    from config.settings import ANALYSIS_YEARS

    series = synthetic.generate_landcover_series(seed=seed)
    years = ANALYSIS_YEARS
    lc_now = series[years[year_idx]]
    lc_next = series[years[year_idx + 1]] if year_idx + 1 < len(years) else series[years[-1]]
    grid = lc_now.shape[0]
    yy, xx = np.mgrid[0:grid, 0:grid]

    deforested_now = lc_now >= 2
    forest_now = lc_now <= 1

    # distances approximatives (transformée de distance par dilatation, voir _edt)
    dist_def = _edt(deforested_now)
    road = np.abs(xx - yy) < 4
    dist_road = _edt(road)
    villages = np.zeros_like(lc_now, dtype=bool)
    for cx, cy in [(int(grid * .3), int(grid * .62)), (int(grid * .7), int(grid * .35))]:
        villages[cy, cx] = True
    dist_vil = _edt(villages)
    topo = synthetic.generate_topography(grid=grid, seed=seed)
    slope, altitude = topo[..., 1], topo[..., 0]
    neighbor_rate = _neighbor_mean(deforested_now.astype(float))

    feats = np.stack([dist_road, dist_vil, dist_def, slope, altitude, neighbor_rate], axis=-1)
    label = ((lc_next >= 2) & forest_now).astype(np.int8)  # forêt qui devient déforestée
    mask = forest_now  # on n'entraîne que sur la forêt encore debout
    return feats[mask], label[mask], feats, forest_now


def _edt(mask: np.ndarray, max_step: int = 40) -> np.ndarray:
    """Distance euclidienne approx. par dilatations 4-connexes."""
    dist = np.full(mask.shape, np.inf, np.float32)
    reached = mask.copy()
    frontier = mask.copy()
    step = 0
    while not reached.all() and step < max_step:
        dist[frontier & np.isinf(dist)] = step
        grown = reached.copy()
        grown[1:, :] |= reached[:-1, :]; grown[:-1, :] |= reached[1:, :]
        grown[:, 1:] |= reached[:, :-1]; grown[:, :-1] |= reached[:, 1:]
        frontier = grown & ~reached
        reached = grown
        step += 1
    dist[np.isinf(dist)] = step
    return dist


def _neighbor_mean(arr: np.ndarray) -> np.ndarray:
    k = np.zeros_like(arr)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            k += np.roll(np.roll(arr, dr, 0), dc, 1)
    return k / 9.0


class RiskPredictor:
    name = "RiskPredictor"

    def __init__(self):
        self.model = self._build()

    def _build(self):
        try:
            from xgboost import XGBClassifier

            return XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.1,
                                 eval_metric="logloss", tree_method="hist")
        except ImportError:
            from sklearn.ensemble import GradientBoostingClassifier

            return GradientBoostingClassifier(random_state=42)

    def train(self, seed: int = 42) -> dict:
        X, y, _, _ = _risk_features(seed=seed)
        if y.sum() == 0:  # garantit au moins deux classes
            y[: max(1, len(y) // 50)] = 1
        self.model.fit(X, y)
        score = float(self.model.score(X, y))
        log.info(f"RiskPredictor entraîné — accuracy train={score:.3f}, positifs={int(y.sum())}")
        return {"train_accuracy": round(score, 4), "n_positive": int(y.sum())}

    def risk_map(self, seed: int = 42) -> np.ndarray:
        """Carte de risque 0–100 sur la zone d'étude."""
        _, _, feats, forest = _risk_features(year_idx=-1, seed=seed)
        flat = feats.reshape(-1, feats.shape[-1])
        try:
            proba = self.model.predict_proba(flat)[:, 1]
        except Exception:
            proba = self.model.predict(flat).astype(float)
        risk = (proba.reshape(forest.shape) * 100).astype(np.float32)
        risk[~forest] = 0
        return risk

    def save(self, path: Path | None = None):
        path = Path(path or MODELS_DIR / "risk_predictor.joblib")
        ensure_dir(path.parent)
        joblib.dump(self.model, path)
        return path


def main() -> None:
    rp = RiskPredictor()
    rp.train()
    rmap = rp.risk_map()
    log.info(f"Carte de risque : min={rmap.min():.1f}, max={rmap.max():.1f}, "
             f"moyenne(forêt)={rmap[rmap > 0].mean():.1f}")


if __name__ == "__main__":
    main()
