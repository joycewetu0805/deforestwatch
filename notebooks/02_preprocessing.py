# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 02 — Pipeline de prétraitement — DeforestWatch-DRC
# Démonstration visuelle du masquage des nuages, des indices spectraux et des
# tuiles 128×128 pour le U-Net.

# %%
import sys, os
sys.path.insert(0, os.path.abspath(".."))
import numpy as np
import matplotlib.pyplot as plt
from src.utils import synthetic
from src.preprocessing import indices, cloud_masking, feature_extraction
from src.visualization.maps import classification_to_rgb

# %% [markdown]
# ## 1. Image Sentinel-2 synthétique (RGB + fausses couleurs NIR)

# %%
lc = synthetic.generate_landcover_series()[2025]
bands = synthetic.landcover_to_bands(lc, seed=2025)
rgb = bands[..., [2, 1, 0]]  # B4,B3,B2
nir = bands[..., [3, 2, 1]]  # NIR en rouge
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
ax[0].imshow(np.clip(rgb * 3, 0, 1)); ax[0].set_title("RGB")
ax[1].imshow(np.clip(nir * 2, 0, 1)); ax[1].set_title("Fausses couleurs NIR")
ax[2].imshow(classification_to_rgb(lc)); ax[2].set_title("Vérité terrain (classes)")
for a in ax: a.axis("off")

# %% [markdown]
# ## 2. Masquage des nuages (avant / après)

# %%
scl = cloud_masking.synthetic_scl(lc.shape, cloud_fraction=0.25)
mask = cloud_masking.cloud_mask_from_scl(scl)
print(f"Pixels valides : {cloud_masking.valid_fraction(mask):.1f} %")

# %% [markdown]
# ## 3. Indices spectraux : forêt vs zone déforestée

# %%
ndvi = indices.ndvi(bands)
print("NDVI moyen forêt :", round(ndvi[lc <= 1].mean(), 3))
print("NDVI moyen déforesté :", round(ndvi[lc >= 2].mean(), 3))

# %% [markdown]
# ## 4. Tuiles 128×128 pour le U-Net

# %%
big = np.tile(bands, (2, 2, 1))
tiles, pos = feature_extraction.extract_tiles(big, tile=128, overlap=32)
print("Nombre de tuiles :", len(tiles), "| forme :", tiles.shape[1:])
