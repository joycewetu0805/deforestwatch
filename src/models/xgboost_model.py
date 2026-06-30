"""
Modèle XGBoost — même interface que le Random Forest pour faciliter la comparaison.
13 features → 5 classes, early stopping, feature importance.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from config.settings import FEATURE_NAMES, MODELS_DIR, XGB_PARAMS
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger

log = get_logger("xgboost_model")


class XGBoostModel:
    name = "XGBoost"

    def __init__(self, **params):
        self.params = {**XGB_PARAMS, **params}
        self.feature_names = FEATURE_NAMES
        self.model = self._build()

    def _build(self):
        try:
            from xgboost import XGBClassifier

            return XGBClassifier(
                objective="multi:softprob",
                tree_method="hist",
                eval_metric="mlogloss",
                **self.params,
            )
        except ImportError:  # repli : GradientBoosting sklearn
            log.warning("xgboost absent → repli GradientBoostingClassifier.")
            from sklearn.ensemble import GradientBoostingClassifier

            return GradientBoostingClassifier(random_state=42)

    def fit(self, X, y, X_val=None, y_val=None):
        try:
            if X_val is not None:
                self.model.fit(X, y, eval_set=[(X_val, y_val)], verbose=False)
            else:
                self.model.fit(X, y)
        except TypeError:
            self.model.fit(X, y)
        log.info(f"{self.name} entraîné sur {len(X)} pixels.")
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)

    def predict_image(self, bands, topo):
        from src.preprocessing.feature_extraction import extract_pixel_features

        H, W = bands.shape[:2]
        X = extract_pixel_features(bands, topo)
        return self.predict(X).reshape(H, W)

    def feature_importance(self) -> dict:
        imp = getattr(self.model, "feature_importances_", np.zeros(len(self.feature_names)))
        return dict(zip(self.feature_names, np.asarray(imp).tolist()))

    def save(self, path: Path | None = None):
        path = Path(path or MODELS_DIR / "xgboost.joblib")
        ensure_dir(path.parent)
        joblib.dump(self.model, path)
        log.info(f"Modèle sauvegardé : {path}")
        return path

    @classmethod
    def load(cls, path: Path):
        obj = cls()
        obj.model = joblib.load(path)
        return obj


def main() -> None:
    from src.utils import synthetic

    ds = synthetic.build_pixel_dataset()
    XGBoostModel().fit(ds["X"][:20000], ds["y"][:20000])


if __name__ == "__main__":
    main()
