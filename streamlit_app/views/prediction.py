"""Page Prédictions — carte de risque de déforestation future."""

from __future__ import annotations

import numpy as np
import streamlit as st

from config.settings import PIXEL_AREA_HA, settings
from src.data import provider
from src.visualization import maps
from streamlit_app.components import ui


@st.cache_data(ttl=600)
def _risk():
    return provider.risk_map()


def render() -> None:
    ui.header("Prédiction des zones à risque",
              "Probabilité de déforestation future par pixel (modèle de risque XGBoost)",
              logo="🔮")

    risk = _risk()
    threshold = st.slider("Seuil de risque minimal affiché", 0, 100, 50)

    masked = np.where(risk >= threshold, risk, 0)
    at_risk_px = int(np.sum(risk >= threshold))
    total_forest_px = int(np.sum(risk > 0))

    c1, c2, c3 = st.columns(3)
    c1.metric("Surface à risque", f"{at_risk_px * PIXEL_AREA_HA:,.0f} ha")
    c2.metric("% de la forêt concernée",
              f"{100 * at_risk_px / max(total_forest_px, 1):.1f} %")
    c3.metric("Risque moyen (forêt)",
              f"{risk[risk > 0].mean():.0f}/100" if (risk > 0).any() else "0")

    st.subheader("Carte de risque (vert = faible, rouge = élevé)")
    st.image(maps.risk_to_rgb(masked), use_column_width=True)

    # ── Zones critiques ──
    st.subheader("⚠️ Zones critiques (risque > 80)")
    ys, xs = np.where(risk > 80)
    if len(ys):
        rng = np.random.default_rng(0)
        sample = rng.choice(len(ys), min(10, len(ys)), replace=False)
        grid = risk.shape[0]
        rows = []
        for i in sample:
            lat = settings.study_area_lat + (ys[i] / grid - 0.5) * 0.45
            lon = settings.study_area_lon + (xs[i] / grid - 0.5) * 0.45
            rows.append({"Latitude": round(lat, 4), "Longitude": round(lon, 4),
                         "Risque": int(risk[ys[i], xs[i]])})
        st.dataframe(sorted(rows, key=lambda r: r["Risque"], reverse=True),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Aucune zone au-dessus du seuil critique.")
