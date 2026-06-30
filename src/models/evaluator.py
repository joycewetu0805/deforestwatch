"""
Évaluateur et comparateur de modèles.
Métriques : Accuracy, Precision, Recall, F1 (macro + par classe), AUC-ROC,
IoU par classe et Mean IoU, matrice de confusion.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from config.settings import LAND_COVER_CLASSES, NUM_CLASSES
from src.utils.logger import get_logger

log = get_logger("evaluator")


def iou_per_class(y_true, y_pred, num_classes=NUM_CLASSES):
    ious = []
    for c in range(num_classes):
        inter = np.sum((y_true == c) & (y_pred == c))
        union = np.sum((y_true == c) | (y_pred == c))
        ious.append(inter / union if union else np.nan)
    return ious


def evaluate(y_true, y_pred, y_proba=None) -> dict:
    """Renvoie un dict de métriques pour un modèle."""
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    ious = iou_per_class(y_true, y_pred)
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision_macro": round(precision_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "recall_macro": round(recall_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "f1_macro": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "mean_iou": round(float(np.nanmean(ious)), 4),
        "iou_per_class": {LAND_COVER_CLASSES[c]: round(float(v), 4) if v == v else None
                          for c, v in enumerate(ious)},
        "f1_per_class": {
            LAND_COVER_CLASSES[c]: round(float(v), 4)
            for c, v in enumerate(f1_score(y_true, y_pred, average=None,
                                           labels=list(range(NUM_CLASSES)), zero_division=0))
        },
    }
    if y_proba is not None:
        try:
            from sklearn.metrics import roc_auc_score

            metrics["auc_roc"] = round(
                roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro"), 4
            )
        except Exception:
            metrics["auc_roc"] = None
    return metrics


def confusion(y_true, y_pred):
    return confusion_matrix(
        np.asarray(y_true).ravel(), np.asarray(y_pred).ravel(),
        labels=list(range(NUM_CLASSES)),
    )


class ModelEvaluator:
    """Agrège les métriques de plusieurs modèles et produit un comparatif."""

    def __init__(self):
        self.results: dict[str, dict] = {}

    def add(self, name: str, y_true, y_pred, y_proba=None):
        self.results[name] = evaluate(y_true, y_pred, y_proba)
        log.info(f"{name} — F1 macro={self.results[name]['f1_macro']}, "
                 f"mean IoU={self.results[name]['mean_iou']}")
        return self.results[name]

    def comparison_table(self) -> pd.DataFrame:
        rows = []
        for name, m in self.results.items():
            rows.append({
                "Modèle": name,
                "Accuracy": m["accuracy"],
                "Precision": m["precision_macro"],
                "Recall": m["recall_macro"],
                "F1-macro": m["f1_macro"],
                "Mean IoU": m["mean_iou"],
                "AUC-ROC": m.get("auc_roc"),
            })
        return pd.DataFrame(rows).sort_values("F1-macro", ascending=False).reset_index(drop=True)

    def best_model(self, metric: str = "f1_macro") -> str:
        return max(self.results, key=lambda k: self.results[k].get(metric, 0))

    def text_report(self) -> str:
        df = self.comparison_table()
        best = self.best_model()
        lines = ["═" * 60, "COMPARAISON DES MODÈLES — DeforestWatch-DRC", "═" * 60,
                 df.to_string(index=False), "", f"Meilleur modèle (F1-macro) : {best}", "═" * 60]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"per_model": self.results, "best_model": self.best_model()}
