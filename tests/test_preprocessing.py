"""Tests du prétraitement : indices, masquage, mosaïques, features."""

import numpy as np

from src.preprocessing import cloud_masking, feature_extraction, indices, mosaic


def test_ndvi_range(sample_bands):
    nd = indices.ndvi(sample_bands)
    assert nd.shape == sample_bands.shape[:2]
    assert np.all(nd >= -1.001) and np.all(nd <= 1.001)


def test_all_indices_shape(sample_bands):
    idx = indices.all_indices(sample_bands)
    assert idx.shape == (*sample_bands.shape[:2], 4)


def test_ndvi_forest_higher_than_bare():
    """Le NDVI de la forêt doit dépasser celui du sol nu."""
    from src.utils import synthetic

    forest = synthetic.landcover_to_bands(np.zeros((16, 16), dtype=np.int8), seed=0)
    bare = synthetic.landcover_to_bands(np.full((16, 16), 2, dtype=np.int8), seed=0)
    assert indices.ndvi(forest).mean() > indices.ndvi(bare).mean()


def test_cloud_mask_and_fraction():
    scl = cloud_masking.synthetic_scl((20, 20), cloud_fraction=0.3, seed=0)
    mask = cloud_masking.cloud_mask_from_scl(scl)
    frac = cloud_masking.valid_fraction(mask)
    assert 50 < frac < 90  # ~70% valides


def test_median_composite_ignores_clouds(sample_bands):
    imgs = [sample_bands.copy() for _ in range(3)]
    masks = [np.ones(sample_bands.shape[:2], bool) for _ in range(3)]
    masks[0][:10] = False  # nuages partiels
    comp = mosaic.median_composite(imgs, masks)
    assert comp.shape == sample_bands.shape
    assert not np.any(np.isnan(comp))


def test_pixel_feature_dimension(sample_bands):
    topo = np.random.rand(*sample_bands.shape[:2], 3).astype(np.float32)
    feats = feature_extraction.extract_pixel_features(sample_bands, topo)
    assert feats.shape[1] == 13  # 6 bandes + 4 indices + 3 topo


def test_tile_extraction_shapes(sample_bands):
    big = np.tile(sample_bands, (8, 8, 1))  # 256x256x6
    labels = np.zeros(big.shape[:2], dtype=np.int8)
    tiles, lab, pos = feature_extraction.extract_tiles(big, labels, tile=128, overlap=32)
    assert tiles.shape[1:] == (128, 128, 6)
    assert lab.shape[1:] == (128, 128)
    assert len(pos) == len(tiles)
