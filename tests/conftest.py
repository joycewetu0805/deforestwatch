"""Fixtures partagées pour la suite de tests."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Base de test isolée, définie avant tout import de config.settings.
# Sans cela, les tests d'authentification écrivent dans la base de démonstration
# et échouent au deuxième lancement, l'utilisateur de test existant déjà.
_TEST_DB = Path(__file__).resolve().parent / ".pytest_deforestwatch.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TEST_DB}")


@pytest.fixture(scope="session", autouse=True)
def _base_de_test_vierge():
    """Repart d'une base vide à chaque session, et ne laisse rien derrière."""
    _TEST_DB.unlink(missing_ok=True)
    yield
    _TEST_DB.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def pixel_dataset():
    from src.utils import synthetic

    return synthetic.build_pixel_dataset()


@pytest.fixture(scope="session")
def tile_dataset():
    from src.utils import synthetic

    return synthetic.build_tile_dataset(n_tiles=8)


@pytest.fixture
def sample_bands():
    """Petit cube de bandes (32,32,6) reproductible."""
    from src.utils import synthetic

    lc = synthetic.generate_landcover_series(grid=32)[2025]
    return synthetic.landcover_to_bands(lc, seed=1)


@pytest.fixture
def api_client():
    """Client de test FastAPI avec base initialisée (events startup)."""
    from fastapi.testclient import TestClient
    from src.api.main import app

    with TestClient(app) as client:
        yield client
