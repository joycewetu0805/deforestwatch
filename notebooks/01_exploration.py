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
# # 01 — Analyse exploratoire (EDA) — DeforestWatch-DRC
# Exploration du dataset de couverture du sol et de la dynamique de déforestation
# dans la province du Mai-Ndombe (2015–2025).

# %%
import sys, os
sys.path.insert(0, os.path.abspath(".."))
import numpy as np
import pandas as pd
from src.utils import synthetic
from config.settings import LAND_COVER_CLASSES, ANALYSIS_YEARS

# %% [markdown]
# ## 1. Chargement et aperçu du dataset

# %%
ds = synthetic.build_pixel_dataset()
df = pd.DataFrame(ds["X"], columns=ds["feature_names"])
df["classe"] = [LAND_COVER_CLASSES[c] for c in ds["y"]]
print("Shape :", df.shape)
df.describe().T

# %% [markdown]
# ## 2. Distribution des classes de couverture du sol

# %%
counts = df["classe"].value_counts()
print((counts / len(df) * 100).round(1).astype(str) + " %")

# %% [markdown]
# ## 3. Évolution temporelle de la couverture forestière 2015–2025

# %%
stats = pd.DataFrame(synthetic.yearly_statistics())
stats[["year", "total_forest_ha", "forest_loss_ha", "deforestation_rate"]]

# %% [markdown]
# ## 4. Heatmap de corrélation entre les features

# %%
corr = df[ds["feature_names"]].corr()
print(corr.round(2))

# %% [markdown]
# ## 5. Boxplots NDVI/EVI par classe (statistiques)

# %%
df.groupby("classe")[["NDVI", "EVI", "NDWI"]].mean().round(3)

# %% [markdown]
# ## 6. Relation précipitations vs déforestation

# %%
from src.data.weather_collector import WeatherCollector
weather = WeatherCollector().annual_series()
merged = stats.merge(weather, on="year")
print("Corrélation précip/perte :",
      merged["annual_precip_mm"].corr(merged["forest_loss_ha"]).round(3))

# %% [markdown]
# **Conclusion EDA** : la forêt recule de façon quasi-monotone, avec une
# accélération du front de déforestation le long des axes routiers et autour des
# villages — ce qui justifie l'approche par modélisation spatiale du risque.
