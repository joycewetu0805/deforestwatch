"""Page Alertes — détection de déforestation + signalement citoyen."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis import alerts as alerts_engine
from streamlit_app.components import ui

SEV_COLOR = {"critique": "#EF4444", "élevée": "#F59E0B", "modérée": "#84CC16"}


@st.cache_data(ttl=300)
def _alerts():
    return [a.to_dict() for a in alerts_engine.detect_alerts()]


@st.cache_data(ttl=300)
def _summary():
    return alerts_engine.summary()


def _save_report(lat, lon, description, reporter):
    """Persiste un signalement en base (même moteur que l'API)."""
    from src.api.database import Report, SessionLocal, init_db

    init_db()
    db = SessionLocal()
    try:
        r = Report(lat=lat, lon=lon, description=description, reporter=reporter or None)
        db.add(r)
        db.commit()
        return True
    finally:
        db.close()


def render() -> None:
    ui.header("Alertes & signalement de déforestation",
              "Détection automatique par secteur + signalement citoyen", logo="🚨")

    s = _summary()
    c1, c2, c3, c4 = st.columns(4)
    ui.kpi(c1, "Alertes actives", str(s["active_alerts"]), delta="dernière année",
           delta_color=ui.ALERT)
    ui.kpi(c2, "Alertes totales", str(s["total_alerts"]), delta_color=ui.AMBER)
    ui.kpi(c3, "Surface perdue signalée", f"{s['total_area_lost_ha']:,.0f} ha",
           delta_color=ui.ALERT)
    ui.kpi(c4, "Année la plus touchée", str(s["worst_year"] or "—"), delta_color=ui.CYAN)

    st.markdown("---")

    alerts = _alerts()
    if not alerts:
        st.info("Aucune alerte au-dessus du seuil.")
    else:
        df = pd.DataFrame(alerts)
        left, right = st.columns([1.1, 1])
        with left:
            st.subheader("📋 Journal des alertes")
            sev = st.multiselect("Filtrer par sévérité",
                                 ["critique", "élevée", "modérée"],
                                 default=["critique", "élevée"])
            years = sorted(df["year"].unique(), reverse=True)
            yr = st.selectbox("Année", ["Toutes"] + [int(y) for y in years])
            fdf = df[df["severity"].isin(sev)] if sev else df
            if yr != "Toutes":
                fdf = fdf[fdf["year"] == yr]
            st.dataframe(
                fdf[["year", "sector", "severity", "area_lost_ha", "lat", "lon"]]
                .rename(columns={"year": "Année", "sector": "Secteur",
                                 "severity": "Sévérité", "area_lost_ha": "Perte (ha)"}),
                use_container_width=True, hide_index=True, height=340,
            )
        with right:
            st.subheader("🗺️ Localisation")
            try:
                import folium
                from streamlit_folium import st_folium
                from config.settings import settings as cfg

                m = folium.Map(location=[cfg.study_area_lat, cfg.study_area_lon],
                               zoom_start=9, tiles="CartoDB dark_matter")
                for a in (fdf if 'fdf' in dir() else df).head(60).to_dict("records"):
                    folium.CircleMarker(
                        [a["lat"], a["lon"]], radius=5,
                        color=SEV_COLOR.get(a["severity"], "#888"), fill=True,
                        fill_opacity=0.8,
                        popup=f"{a['sector']} · {a['year']} · {a['area_lost_ha']} ha",
                    ).add_to(m)
                st_folium(m, height=340, use_container_width=True)
            except Exception:
                st.map(fdf.rename(columns={"lat": "latitude", "lon": "longitude"})
                       [["latitude", "longitude"]])

    # ── Formulaire de signalement ──
    st.markdown("---")
    st.subheader("📣 Signaler une déforestation")
    st.caption("Ouvert à tous : signalez une coupe ou un défrichement suspect.")
    with st.form("report", clear_on_submit=True):
        cc1, cc2 = st.columns(2)
        lat = cc1.number_input("Latitude", value=-1.95, format="%.4f")
        lon = cc2.number_input("Longitude", value=18.27, format="%.4f")
        desc = st.text_area("Description", placeholder="Ce que vous avez observé…")
        reporter = st.text_input("Votre email (optionnel)")
        sent = st.form_submit_button("🚨 Envoyer le signalement", type="primary",
                                     use_container_width=True)
    if sent:
        if len(desc.strip()) < 3:
            st.error("Merci de décrire ce que vous avez observé.")
        else:
            _save_report(lat, lon, desc.strip(), reporter.strip())
            st.success("✅ Signalement enregistré. Merci pour votre contribution !")
            st.balloons()
