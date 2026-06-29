"""Page Dashboard — vue d'ensemble (KPIs, carte, évolution, top zones)."""

from __future__ import annotations

import numpy as np
import streamlit as st

from config.settings import PIXEL_AREA_HA
from src.utils import synthetic
from src.visualization import charts, maps, timeline


@st.cache_data(ttl=600)
def _stats():
    return synthetic.yearly_statistics()


@st.cache_data(ttl=600)
def _risk():
    return synthetic.risk_map()


def render() -> None:
    st.title("📊 Dashboard — Surveillance de la déforestation")
    st.caption("Province du Mai-Ndombe (Inongo), RDC · Composites Sentinel-2 2015–2025")

    stats = _stats()
    last, first = stats[-1], stats[0]
    total_loss = sum(s["forest_loss_ha"] for s in stats)

    # ── KPIs ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Surface forestière actuelle", f"{last['total_forest_ha']:,.0f} ha")
    c2.metric("Perte totale 2015–2025", f"{total_loss:,.0f} ha",
              delta=f"-{100 * total_loss / first['total_forest_ha']:.1f} %", delta_color="inverse")
    c3.metric("Taux annuel moyen",
              f"{np.mean([s['deforestation_rate'] for s in stats[1:]]):.2f} %")
    risk = _risk()
    c4.metric("Zones à risque élevé", f"{int(np.sum(risk > 70)) * PIXEL_AREA_HA:,.0f} ha")

    st.markdown("---")

    # ── Carte + évolution ──
    left, right = st.columns([1, 1])
    with left:
        st.subheader("🗺️ Zone d'étude")
        try:
            from streamlit_folium import st_folium

            st_folium(maps.study_area_map(), height=380, use_container_width=True)
        except Exception:
            st.info("Carte interactive indisponible (installez streamlit-folium).")
            st.image(maps.risk_to_rgb(risk), caption="Carte de risque (vert→rouge)",
                     use_column_width=True)
    with right:
        st.subheader("📉 Évolution forestière")
        st.plotly_chart(charts.forest_evolution(stats), use_container_width=True)

    # ── Perte annuelle + timeline ──
    a, b = st.columns(2)
    a.plotly_chart(charts.annual_loss_bar(stats), use_container_width=True)
    b.plotly_chart(timeline.deforestation_timeline(stats), use_container_width=True)

    # ── Top 5 zones ──
    st.subheader("🔥 Top 5 des secteurs les plus touchés")
    series = synthetic.generate_landcover_series()
    lc = series[max(series)]
    grid = lc.shape[0]
    block = grid // 5
    rows = []
    for bi in range(5):
        for bj in range(5):
            sub = lc[bi * block:(bi + 1) * block, bj * block:(bj + 1) * block]
            loss_px = int(np.sum(sub >= 2))
            rows.append({"Secteur": f"R{bi}C{bj}", "Déforesté (ha)": round(loss_px * PIXEL_AREA_HA, 1)})
    rows = sorted(rows, key=lambda r: r["Déforesté (ha)"], reverse=True)[:5]
    st.dataframe(rows, use_container_width=True, hide_index=True)
