"""Page Dashboard — vue d'ensemble (KPIs, carte, évolution, top zones)."""

from __future__ import annotations

import numpy as np
import streamlit as st

from config.settings import PIXEL_AREA_HA
from src.data import provider
from src.visualization import charts, maps, timeline
from streamlit_app.components import ui


@st.cache_data(ttl=600)
def _stats():
    return provider.yearly_statistics()


@st.cache_data(ttl=600)
def _risk():
    return provider.risk_map()


@st.cache_data(ttl=600)
def _series_cached():
    return provider.landcover_series()


@st.cache_data(ttl=600)
def _carbon():
    from src.analysis import carbon
    return carbon.summary(), carbon.yearly_carbon()


@st.cache_data(ttl=600)
def _radar_coverage():
    from src.data.radar import cloud_penetration_demo
    from config.settings import ANALYSIS_YEARS
    return cloud_penetration_demo(ANALYSIS_YEARS[-1])


def _carbon_impact():
    st.subheader("🌍 Impact climatique — émissions de CO₂")
    s, yearly = _carbon()
    eq = s["equivalents"]
    c1, c2, c3, c4 = st.columns(4)
    ui.kpi(c1, "CO₂ total émis", f"{s['total_co2_mt']:,.1f} Mt",
           delta="depuis la déforestation 2015–2025", delta_color=ui.ALERT)
    ui.kpi(c2, "Équivalent voitures", f"{eq['cars_year']:,}",
           delta="voitures pendant 1 an", delta_color=ui.AMBER)
    ui.kpi(c3, "Arbres pour compenser", f"{eq['trees_year'] / 1e6:,.0f} M",
           delta="arbres · 1 an", delta_color=ui.EMERALD)
    rc = _radar_coverage()
    ui.kpi(c4, "Atout radar (Sentinel-1)", f"+{rc['gain_pct']:.0f} %",
           delta=f"pixels vs optique ({rc['optical_usable_pct']:.0f}% sous nuages)",
           delta_color=ui.CYAN)
    st.caption(f"Hypothèse : {s['assumptions']['co2_t_per_ha']:.0f} t CO₂/ha "
               "(biomasse aérienne forêt tropicale du Bassin du Congo · IPCC).")


def _time_machine(stats):
    """Time-lapse : la forêt qui recule, avec curseur d'année et comparateur 2015."""
    st.subheader("🛰️ Machine à remonter le temps — la forêt disparaît sous vos yeux")
    series = _series_cached()
    years = sorted(series.keys())
    by_year = {s["year"]: s for s in stats}

    year = st.select_slider("Glissez les années", options=years, value=years[-1],
                            key="tm_year")
    cur = by_year.get(year, stats[-1])
    first = stats[0]
    loss_pct = (1 - cur["total_forest_ha"] / first["total_forest_ha"]) * 100

    c1, c2, c3 = st.columns([1, 1, 1])
    c1.image(maps.classification_to_rgb(series[years[0]]),
             caption=f"{years[0]} — référence", use_column_width=True)
    c2.image(maps.classification_to_rgb(series[year]),
             caption=f"{year} — sélection", use_column_width=True)
    with c3:
        ui.kpi(c3, f"Surface forestière — {year}",
               f"{cur['total_forest_ha']:,.0f} ha",
               delta=f"▼ {loss_pct:.1f} % perdus depuis {years[0]}", delta_color=ui.ALERT)
        st.progress(min(loss_pct / 100, 1.0))
        st.caption(" · ".join(f"{v}" for v in [
            "🟩 Forêt dense", "🟨 Dégradée", "🟧 Agriculture", "🟦 Eau", "🟥 Bâti"]))


def render() -> None:
    ui.header("Surveillance de la forêt équatoriale",
              "Province du Mai-Ndombe (Inongo) · Bassin du Congo · Sentinel-2 2015–2025",
              logo="📊")
    ui.source_badge(provider.is_real())

    stats = _stats()
    last, first = stats[-1], stats[0]
    total_loss = sum(s["forest_loss_ha"] for s in stats)
    risk = _risk()

    # ── KPIs ──
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    ui.kpi(c1, "Surface forestière actuelle", f"{last['total_forest_ha']:,.0f} ha")
    ui.kpi(c2, "Perte totale 2015–2025", f"{total_loss:,.0f} ha",
           delta=f"▼ {100 * total_loss / first['total_forest_ha']:.1f} % depuis 2015",
           delta_color=ui.ALERT)
    ui.kpi(c3, "Taux annuel moyen",
           f"{np.mean([s['deforestation_rate'] for s in stats[1:]]):.2f} %", delta_color=ui.AMBER)
    ui.kpi(c4, "Zones à risque élevé", f"{int(np.sum(risk > 70)) * PIXEL_AREA_HA:,.0f} ha",
           delta="risque > 70/100", delta_color=ui.CYAN)

    st.markdown("---")

    # ── Impact climatique (carbone) ──
    _carbon_impact()

    st.markdown("---")

    # ── Machine à remonter le temps ──
    _time_machine(stats)

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
    series = provider.landcover_series()
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
