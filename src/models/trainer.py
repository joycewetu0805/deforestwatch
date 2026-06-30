"""
Pipeline d'entraînement unifié.
Charge les datasets, entraîne RF / XGBoost / U-Net, évalue sur le test set,
sauvegarde les modèles et génère un rapport JSON de métriques.

Exécution : python -m src.models.trainer
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from config.settings import MODELS_DIR, PROCESSED_DIR
from src.data.dataset_builder import build_pixel_splits, build_tile_splits
from src.models.evaluator import ModelEvaluator
from src.models.random_forest import RandomForestModel
from src.models.risk_predictor import RiskPredictor
from src.models.unet import UNetModel
from src.models.xgboost_model import XGBoostModel
from src.utils.helpers import ensure_dir, save_json
from src.utils.logger import get_logger

log = get_logger("trainer")


def _subsample(X, y, n, seed=42):
    if len(X) <= n:
        return X, y
    idx = np.random.default_rng(seed).choice(len(X), n, replace=False)
    return X[idx], y[idx]


def train_all(quick: bool = True, out_dir: Path = MODELS_DIR) -> dict:
    ensure_dir(out_dir)
    evaluator = ModelEvaluator()

    # ── Données pixel-based (RF / XGBoost) ──
    log.info("Chargement du dataset pixel-based…")
    pix = build_pixel_splits()
    cap = 30000 if quick else len(pix["X_train"])
    Xtr, ytr = _subsample(pix["X_train"], pix["y_train"], cap)
    Xte, yte = pix["X_test"], pix["y_test"]

    # Random Forest
    rf = RandomForestModel().fit(Xtr, ytr)
    evaluator.add("RandomForest", yte, rf.predict(Xte), rf.predict_proba(Xte))
    rf.save(out_dir / "random_forest.joblib")

    # XGBoost
    xgb = XGBoostModel().fit(Xtr, ytr)
    try:
        proba = xgb.predict_proba(Xte)
    except Exception:
        proba = None
    evaluator.add("XGBoost", yte, xgb.predict(Xte), proba)
    xgb.save(out_dir / "xgboost.joblib")

    # ── Données tile-based (U-Net) ──
    log.info("Chargement du dataset tile-based…")
    tiles = build_tile_splits()
    unet = UNetModel().fit(
        tiles["X_train"], tiles["y_train"],
        tiles["X_val"], tiles["y_val"],
        epochs=2 if quick else None,
    )
    unet_pred = unet.predict(tiles["X_test"])
    evaluator.add("U-Net", tiles["y_test"], unet_pred)
    unet.save()

    # ── Prédiction de risque ──
    risk = RiskPredictor()
    risk_info = risk.train()
    risk.save()

    # ── Rapport ──
    report = evaluator.to_dict()
    report["risk_predictor"] = risk_info
    report["comparison"] = evaluator.comparison_table().to_dict(orient="records")
    save_json(report, PROCESSED_DIR / "model_metrics.json")
    log.info("\n" + evaluator.text_report())
    log.info(f"Rapport sauvegardé → {PROCESSED_DIR / 'model_metrics.json'}")
    return report


def main() -> None:
    train_all(quick=True)


if __name__ == "__main__":
    main()
