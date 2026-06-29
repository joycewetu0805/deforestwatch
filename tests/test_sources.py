"""Tests de la couche source de données (synthétique + chemin données réelles)."""

import numpy as np

from src.data import provider
from src.data.sources import DataSource, RasterSource, SyntheticSource, resolve_source


def test_demo_mode_uses_synthetic():
    src = resolve_source(force=None, use_cache=False)
    assert src.name == "synthetic"
    assert not src.is_real


def test_set_mode_switches_and_falls_back():
    from src.data.sources import set_mode

    try:
        # 'real' sans données dans data/raw → repli synthétique mais mode mémorisé
        set_mode("real")
        assert provider.mode() == "real"
        assert provider.is_real() is False          # repli (pas de data/raw)
        assert provider.info()["mode"] == "real"

        set_mode("demo")
        assert provider.mode() == "demo"
        assert provider.source_name() == "synthetic"
    finally:
        set_mode("auto")                            # restaure l'état par défaut
    assert provider.mode() == "auto"


def test_synthetic_source_shapes():
    src = SyntheticSource()
    y = src.years()[-1]
    assert src.composite(y).shape[-1] == 6
    assert src.landcover(y).shape == src.composite(y).shape[:2]
    assert src.topography().shape[-1] == 3


def test_raster_source_no_data_detection(tmp_path):
    assert RasterSource.has_data(tmp_path) is False


def test_describe_source_keys():
    info = provider.info()
    for k in ["source", "is_real", "years", "ecosystem"]:
        assert k in info
    assert "équatoriale" in info["ecosystem"]


class _FakeRealSource(DataSource):
    """Source 'réelle' simulée (sans rasterio) pour valider la plomberie."""

    name = "fake_raster"
    is_real = True

    def __init__(self, grid=64, years=(2020, 2021, 2022)):
        self.grid = grid
        self._years = list(years)
        rng = np.random.default_rng(0)
        self._lc = {y: rng.integers(0, 5, (grid, grid)).astype(np.int16) for y in years}

    def years(self):
        return self._years

    def composite(self, year):
        rng = np.random.default_rng(year)
        return rng.random((self.grid, self.grid, 6)).astype(np.float32)

    def landcover(self, year):
        return self._lc[year]

    def topography(self):
        return np.zeros((self.grid, self.grid, 3), dtype=np.float32)


def test_pipeline_runs_on_real_like_source(monkeypatch):
    """Le builder de dataset et les stats fonctionnent sur une source 'réelle'."""
    fake = _FakeRealSource()
    monkeypatch.setattr(provider, "source", lambda: fake)

    from src.data.dataset_builder import build_pixel_splits

    splits = build_pixel_splits()
    assert splits["X_train"].shape[1] == 13          # 6 bandes + 4 indices + 3 topo
    assert set(np.unique(splits["y_train"])).issubset(set(range(5)))

    stats = provider.yearly_statistics()
    assert len(stats) == len(fake.years())
    assert provider.is_real() is True
