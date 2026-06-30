"""Tests des modèles : entraînement, prédiction, métriques."""

import numpy as np

from src.models.evaluator import ModelEvaluator, evaluate, iou_per_class
from src.models.random_forest import RandomForestModel
from src.models.risk_predictor import RiskPredictor
from src.models.xgboost_model import XGBoostModel


def _small(pixel_dataset, n=4000):
    X, y = pixel_dataset["X"][:n], pixel_dataset["y"][:n]
    return X, y


def test_random_forest_fit_predict(pixel_dataset):
    X, y = _small(pixel_dataset)
    rf = RandomForestModel(n_estimators=30).fit(X, y)
    pred = rf.predict(X[:100])
    assert pred.shape == (100,)
    assert set(np.unique(pred)).issubset(set(range(5)))


def test_random_forest_feature_importance(pixel_dataset):
    X, y = _small(pixel_dataset)
    rf = RandomForestModel(n_estimators=30).fit(X, y)
    imp = rf.feature_importance()
    assert len(imp) == 13
    assert abs(sum(imp.values()) - 1.0) < 0.05


def test_xgboost_fit_predict(pixel_dataset):
    X, y = _small(pixel_dataset)
    xgb = XGBoostModel().fit(X, y)
    pred = xgb.predict(X[:50])
    assert pred.shape == (50,)


def test_evaluate_metrics_keys():
    y_true = np.array([0, 1, 2, 3, 4, 0, 1])
    y_pred = np.array([0, 1, 2, 3, 4, 0, 2])
    m = evaluate(y_true, y_pred)
    for k in ["accuracy", "f1_macro", "mean_iou", "precision_macro", "recall_macro"]:
        assert k in m
    assert 0 <= m["accuracy"] <= 1


def test_iou_perfect():
    y = np.array([0, 1, 2, 3, 4])
    ious = iou_per_class(y, y)
    assert all(v == 1.0 for v in ious)


def test_model_evaluator_comparison(pixel_dataset):
    X, y = _small(pixel_dataset)
    ev = ModelEvaluator()
    rf = RandomForestModel(n_estimators=30).fit(X, y)
    ev.add("RF", y[:500], rf.predict(X[:500]))
    df = ev.comparison_table()
    assert "F1-macro" in df.columns
    assert ev.best_model() == "RF"


def test_risk_predictor_map():
    rp = RiskPredictor()
    rp.train()
    rmap = rp.risk_map()
    assert rmap.min() >= 0 and rmap.max() <= 100
