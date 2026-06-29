"""
Construction du dataset final ML à partir des composites GEE, Hansen, SRTM et météo.

Produit deux datasets :
  - pixel-based  (RF / XGBoost)  : X (N,13), y (N,)
  - tile-based   (U-Net)         : X (N,128,128,6), y (N,128,128)

Split train/val/test 70/15/15 avec stratification spatiale (blocs) pour éviter
le data leakage géographique.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from config.settings import GRID_SIZE, PROCESSED_DIR
from src.utils.helpers import ensure_dir, save_json
from src.utils.logger import get_logger
from src.utils import synthetic

log = get_logger("dataset_builder")


def spatial_block_split(grid: int = GRID_SIZE, seed: int = 42):
    """
    Découpe la grille en blocs et assigne chaque bloc à train/val/test.
    Renvoie un masque (grid,grid) avec valeurs 0=train, 1=val, 2=test.
    """
    rng = np.random.default_rng(seed)
    n_blocks = 8
    block = grid // n_blocks
    assign = np.zeros((grid, grid), dtype=np.int8)
    for bi in range(n_blocks):
        for bj in range(n_blocks):
            r = rng.random()
            split = 0 if r < 0.70 else (1 if r < 0.85 else 2)
            assign[bi * block:(bi + 1) * block, bj * block:(bj + 1) * block] = split
    return assign


def build_pixel_splits(seed: int = 42) -> dict:
    """Dataset pixel-based avec split spatial."""
    from config.settings import FEATURE_NAMES

    series = synthetic.generate_landcover_series(seed=seed)
    from config.settings import ANALYSIS_YEARS

    year = ANALYSIS_YEARS[-1]
    lc = series[year]
    bands = synthetic.landcover_to_bands(lc, seed=year)
    idx = synthetic.compute_indices_array(bands)
    topo = synthetic.generate_topography(seed=seed)
    feats = np.concatenate([bands, idx, topo], axis=-1)  # (H,W,13)

    assign = spatial_block_split(seed=seed).reshape(-1)
    X = feats.reshape(-1, feats.shape[-1])
    y = lc.reshape(-1)

    out = {"feature_names": FEATURE_NAMES}
    for name, code in [("train", 0), ("val", 1), ("test", 2)]:
        m = assign == code
        out[f"X_{name}"], out[f"y_{name}"] = X[m], y[m]
    return out


def build_tile_splits(seed: int = 42) -> dict:
    """Dataset tile-based (U-Net) avec split aléatoire des tuiles."""
    ds = synthetic.build_tile_dataset(n_tiles=96, seed=seed)
    X, y = ds["X"], ds["y"]
    n = len(X)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_tr, n_val = int(0.70 * n), int(0.15 * n)
    tr, va, te = perm[:n_tr], perm[n_tr:n_tr + n_val], perm[n_tr + n_val:]
    return {
        "X_train": X[tr], "y_train": y[tr],
        "X_val": X[va], "y_val": y[va],
        "X_test": X[te], "y_test": y[te],
    }


def export(out_dir: Path = PROCESSED_DIR, seed: int = 42) -> dict:
    """Construit et sauvegarde les deux datasets sur disque."""
    ensure_dir(out_dir)
    pixel = build_pixel_splits(seed)
    tile = build_tile_splits(seed)

    np.savez_compressed(
        out_dir / "pixel_dataset.npz",
        **{k: v for k, v in pixel.items() if k != "feature_names"},
    )
    np.savez_compressed(out_dir / "tile_dataset.npz", **tile)

    meta = {
        "feature_names": pixel["feature_names"],
        "pixel_train": int(len(pixel["y_train"])),
        "pixel_val": int(len(pixel["y_val"])),
        "pixel_test": int(len(pixel["y_test"])),
        "tile_train": int(len(tile["X_train"])),
        "tile_val": int(len(tile["X_val"])),
        "tile_test": int(len(tile["X_test"])),
    }
    save_json(meta, out_dir / "dataset_metadata.json")
    log.info(f"Datasets exportés dans {out_dir} : {meta}")
    return meta


def main() -> None:
    export()


if __name__ == "__main__":
    main()
