"""Fixtures partagées pour la suite de tests."""

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Base de test isolée (fichier temporaire) : évite de polluer data/ et garantit
# des tests déterministes, indépendants de l'état laissé par une exécution
# précédente. Doit être défini AVANT tout import de config/settings ou src.
os.environ.setdefault(
    "DATABASE_URL", f"sqlite:///{Path(tempfile.gettempdir()) / 'dfw_test.db'}"
)


@pytest.fixture(autouse=True)
def _isolate_db():
    """Repart d'un schéma vierge à chaque test (isolation déterministe)."""
    from src.api.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


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
