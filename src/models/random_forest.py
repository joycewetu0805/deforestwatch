"""
Modèle Random Forest — baseline pixel-based (13 features → 5 classes).
Validation croisée stratifiée, GridSearchCV optionnel, feature importance.
"""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from config.settings import FEATURE_NAMES, MODELS_DIR, RF_PARAMS
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger

log = get_logger("random_forest")


class RandomForestModel:
    name = "RandomForest"

    def __init__(self, **params):
        self.params = {**RF_PARAMS, **params}
        self.model = RandomForestClassifier(**self.params)
        self.feature_names = FEATURE_NAMES

    def fit(self, X, y, tune: bool = False):
        if tune:
            grid = {
                "n_estimators": [100, 200],
                "max_depth": [10, 15, 20],
                "min_samples_split": [2, 5],
            }
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            search = GridSearchCV(
                RandomForestClassifier(random_state=42, n_jobs=-1),
                grid, cv=cv, scoring="f1_macro", n_jobs=-1,
            )
            search.fit(X, y)
            self.model = search.best_estimator_
            log.info(f"GridSearch meilleurs params : {search.best_params_}")
        else:
            self.model.fit(X, y)
        log.info(f"{self.name} entraîné sur {len(X)} pixels.")
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)

    def predict_image(self, bands, topo):
        """Classifie une image complète. bands (H,W,6), topo (H,W,3) -> (H,W)."""
        from src.preprocessing.feature_extraction import extract_pixel_features

        H, W = bands.shape[:2]
        X = extract_pixel_features(bands, topo)
        return self.predict(X).reshape(H, W)

    def feature_importance(self) -> dict:
        return dict(zip(self.feature_names, self.model.feature_importances_.tolist()))

    def save(self, path: Path | None = None):
        path = Path(path or MODELS_DIR / "random_forest.joblib")
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
    rf = RandomForestModel().fit(ds["X"][:20000], ds["y"][:20000])
    log.info(f"Importances : {rf.feature_importance()}")


if __name__ == "__main__":
    main()
