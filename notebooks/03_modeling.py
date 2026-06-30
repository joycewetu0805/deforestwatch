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
# # 03 — Modélisation et comparaison — DeforestWatch-DRC
# Entraînement de Random Forest, XGBoost et U-Net, puis comparaison des
# performances (le tableau qui synthétise les résultats pour le mémoire).

# %%
import sys, os
sys.path.insert(0, os.path.abspath(".."))
import numpy as np
from src.data.dataset_builder import build_pixel_splits, build_tile_splits
from src.models.random_forest import RandomForestModel
from src.models.xgboost_model import XGBoostModel
from src.models.unet import UNetModel
from src.models.evaluator import ModelEvaluator, confusion

# %% [markdown]
# ## 1. Chargement des datasets

# %%
pix = build_pixel_splits()
Xtr, ytr = pix["X_train"][:30000], pix["y_train"][:30000]
Xte, yte = pix["X_test"], pix["y_test"]
tiles = build_tile_splits()
print("Pixels train :", len(Xtr), "| test :", len(Xte))

# %% [markdown]
# ## 2. Entraînement des trois modèles

# %%
ev = ModelEvaluator()
rf = RandomForestModel().fit(Xtr, ytr)
ev.add("RandomForest", yte, rf.predict(Xte), rf.predict_proba(Xte))

xgb = XGBoostModel().fit(Xtr, ytr)
ev.add("XGBoost", yte, xgb.predict(Xte))

unet = UNetModel().fit(tiles["X_train"], tiles["y_train"], epochs=2)
ev.add("U-Net", tiles["y_test"], unet.predict(tiles["X_test"]))

# %% [markdown]
# ## 3. Tableau comparatif des performances

# %%
print(ev.text_report())

# %% [markdown]
# ## 4. Feature importance (Random Forest)

# %%
imp = sorted(rf.feature_importance().items(), key=lambda x: -x[1])
for name, val in imp:
    print(f"{name:>10} : {val:.3f}")

# %% [markdown]
# ## 5. Matrice de confusion du meilleur modèle pixel-based

# %%
print(confusion(yte, rf.predict(Xte)))
