"""
Tests du branchement de la carte de risque sur le modèle entraîné.

Le point vérifié : `provider.risk_map()` sert le prédicteur appris quand il est
présent sur le disque, et la référence géométrique sinon, sans que l'appelant
ait à changer quoi que ce soit.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.data import provider
from src.models.risk_predictor import RiskPredictor, _risk_features
from src.utils import synthetic


@pytest.fixture(autouse=True)
def _cache_propre():
    """Chaque test repart d'un provider qui n'a pas encore résolu le modèle."""
    provider.reset_risk_model()
    yield
    provider.reset_risk_model()


def test_risk_map_a_toujours_la_forme_de_la_grille():
    risk = provider.risk_map()
    assert risk.ndim == 2
    assert risk.shape[0] == risk.shape[1]
    assert risk.min() >= 0 and risk.max() <= 100


def test_source_est_declaree():
    assert provider.risk_source() in {"model", "baseline"}
    assert provider.risk_source_label()


def test_repli_quand_aucun_modele(monkeypatch):
    monkeypatch.setattr("src.models.risk_predictor.is_trained", lambda: False)
    provider.reset_risk_model()
    assert provider.risk_source() == "baseline"
    attendu = synthetic.risk_map(series=provider.landcover_series())
    assert np.array_equal(provider.risk_map(), attendu)


def test_le_modele_est_servi_quand_il_existe(monkeypatch, tmp_path):
    """Entraîne un modèle jetable, puis vérifie que le provider le sert."""
    modele = RiskPredictor()
    modele.train()
    chemin = modele.save(tmp_path / "risk_predictor.joblib")

    monkeypatch.setattr("src.models.risk_predictor.is_trained", lambda: True)
    monkeypatch.setattr("src.models.risk_predictor.default_model_path", lambda: chemin)
    provider.reset_risk_model()

    assert provider.risk_source() == "model"
    risk = provider.risk_map()
    baseline = synthetic.risk_map(series=provider.landcover_series())
    assert risk.shape == baseline.shape
    assert not np.array_equal(risk, baseline), \
        "le modèle doit produire autre chose que la référence géométrique"


def test_repli_si_le_modele_est_illisible(monkeypatch, tmp_path):
    corrompu = tmp_path / "risk_predictor.joblib"
    corrompu.write_bytes(b"pas un modele joblib")
    monkeypatch.setattr("src.models.risk_predictor.is_trained", lambda: True)
    monkeypatch.setattr("src.models.risk_predictor.default_model_path", lambda: corrompu)
    provider.reset_risk_model()

    assert provider.risk_source() == "baseline"
    assert provider.risk_map().shape[0] > 0


def test_risque_nul_hors_foret():
    """Le risque ne porte que sur la forêt encore debout."""
    risk = provider.risk_map()
    lc = provider.landcover_series()[max(provider.landcover_series())]
    hors_foret = lc >= 2
    assert np.all(risk[hors_foret] == 0)


def test_features_acceptent_une_serie_injectee():
    """Le module de risque ne doit pas dépendre du générateur synthétique."""
    serie = synthetic.generate_landcover_series(seed=7)
    X, y, feats, forest = _risk_features(series=serie)
    assert X.shape[1] == 6
    assert len(X) == len(y)
    assert feats.shape[:2] == forest.shape
