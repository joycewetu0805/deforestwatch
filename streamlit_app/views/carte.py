"""
Page Carte — carte interactive 2D/3D sur fond de carte réel.

Les autres vues affichent des images statiques. Celle-ci pose les sorties du
pipeline sur un fond de carte navigable : zoom, déplacement, rotation,
inclinaison. En 3D, chaque cellule devient une colonne dont la hauteur et la
couleur suivent la valeur affichée.

Rendu par pydeck, qui expose deck.gl et est livré avec Streamlit.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from config.settings import PIXEL_AREA_HA
from src.data import provider
from src.visualization import geo
from streamlit_app.components import ui

# Fonds de carte CARTO : pas de jeton Mapbox requis.
BASEMAPS = {
    "Sombre": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    "Clair": "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    "Voyager": "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
}

LAYERS = {
    "Risque de déforestation": "risk",
    "Couverture du sol": "landcover",
    "Pertes depuis 2015": "loss",
}

TOOLTIP_STYLE = {"backgroundColor": "#0f172a", "color": "#f8fafc",
                 "fontSize": "12px", "borderRadius": "6px", "padding": "8px 10px"}


@st.cache_data(ttl=600, show_spinner=False)
def _series() -> dict:
    return provider.landcover_series()


@st.cache_data(ttl=600, show_spinner=False)
def _risk() -> np.ndarray:
    return provider.risk_map()


@st.cache_data(ttl=600, show_spinner=False)
def _cells(layer: str, year: int, step: int, min_risk: float) -> list[dict]:
    """Cellules de la couche demandée. Mise en cache : l'agrégation est coûteuse."""
    series = _series()
    years = sorted(series)
    if layer == "landcover":
        return geo.landcover_cells(series[year], step=step)
    if layer == "loss":
        return geo.loss_cells(series[years[0]], series[year], step=step)
    return geo.risk_cells(_risk(), step=step, min_risk=min_risk)


def _tooltip(layer: str, step: int) -> dict:
    surface = f"{geo.cell_area_ha(step):,.0f} ha".replace(",", " ")
    if layer == "risk":
        html = (f"<b>Risque {{value}}/100</b><br/>Cellule de {surface}"
                "<br/><span style='color:#94a3b8'>{lat}, {lon}</span>")
    elif layer == "landcover":
        html = (f"<b>{{label}}</b><br/>Cellule de {surface}"
                "<br/><span style='color:#94a3b8'>{lat}, {lon}</span>")
    else:
        html = ("<b>{label}</b><br/>{value} ha perdus"
                "<br/><span style='color:#94a3b8'>{lat}, {lon}</span>")
    return {"html": html, "style": TOOLTIP_STYLE}


def render() -> None:
    ui.header("Carte interactive",
              "Les sorties du pipeline posées sur un fond de carte réel, en 2D ou en 3D",
              logo="🗺️")

    series = _series()
    years = sorted(series)

    c1, c2, c3 = st.columns([2.2, 2.4, 1.2])
    layer_label = c1.selectbox("Couche affichée", list(LAYERS), index=0)
    layer = LAYERS[layer_label]
    year = c2.select_slider("Année", options=years, value=years[-1],
                            disabled=(layer == "risk"),
                            help="Le risque porte sur l'état le plus récent."
                                 if layer == "risk" else None)
    mode = c3.radio("Vue", ["3D", "2D"], horizontal=True)

    with st.expander("Réglages d'affichage"):
        s1, s2, s3 = st.columns(3)
        basemap = s1.selectbox("Fond de carte", list(BASEMAPS), index=0)
        step = s2.select_slider(
            "Finesse", options=[8, 6, 4, 3, 2], value=4,
            help="Taille des cellules en pixels d'origine. Plus la valeur est "
                 "basse, plus la carte est fine et lourde à afficher.",
        )
        height_scale = s3.slider("Échelle des hauteurs", 0.2, 3.0, 1.0, step=0.1,
                                 disabled=(mode == "2D"))
        min_risk = s1.slider("Risque minimal affiché", 0, 90, 5,
                             disabled=(layer != "risk"))
        opacity = s2.slider("Opacité", 0.3, 1.0, 0.85, step=0.05)

    cells = _cells(layer, year, step, float(min_risk))
    if not cells:
        st.warning("Aucune cellule à afficher avec ces réglages.")
        return

    extruded = mode == "3D"
    layers = [
        pdk.Layer(
            "ColumnLayer",
            data=cells,
            get_position=["lon", "lat"],
            get_elevation="height",
            elevation_scale=height_scale if extruded else 0,
            radius=geo.cell_radius_m(_risk().shape, step),
            get_fill_color="color",
            disk_resolution=4,      # cellules carrées, elles pavent la zone
            angle=45,
            coverage=1.0,
            extruded=extruded,
            pickable=True,
            auto_highlight=True,
            opacity=opacity,
        )
    ]

    lat, lon = geo.center()
    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=pdk.ViewState(
                latitude=lat, longitude=lon, zoom=9.3,
                pitch=45 if extruded else 0, bearing=0,
            ),
            map_style=BASEMAPS[basemap],
            tooltip=_tooltip(layer, step),
        ),
        use_container_width=True,
    )

    st.caption("Molette pour zoomer, clic-glissé pour déplacer, "
               "Ctrl + clic-glissé pour pivoter et incliner. "
               "Survolez une cellule pour lire sa valeur.")
    if layer == "risk":
        st.caption(f"Source du risque : {provider.risk_source_label()}.")

    _legend(layer)
    _indicators(series, years, year)


def _legend(layer: str) -> None:
    items = geo.legend()[layer]
    chips = "".join(
        "<span style='display:inline-flex;align-items:center;gap:6px;"
        "margin-right:16px;font-size:.82rem;'>"
        f"<span style='width:13px;height:13px;border-radius:3px;"
        f"background:{i['color']};display:inline-block;'></span>{i['label']}</span>"
        for i in items
    )
    prefix = "Score de risque&nbsp;: " if layer == "risk" else ""
    st.markdown(f"<div style='margin:2px 0 14px;color:#94A3B8;'>{prefix}{chips}</div>",
                unsafe_allow_html=True)


def _indicators(series: dict, years: list[int], year: int) -> None:
    lc = series[year]
    risk = _risk()
    forest_start = (series[years[0]] == 0) | (series[years[0]] == 1)
    forest_now = (lc == 0) | (lc == 1)

    forest_ha = float(np.sum(forest_now)) * PIXEL_AREA_HA
    lost_ha = float(np.sum(forest_start & ~forest_now)) * PIXEL_AREA_HA
    high_ha = float(np.sum(risk > 70)) * PIXEL_AREA_HA

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Forêt en {year}", f"{forest_ha:,.0f} ha".replace(",", " "))
    c2.metric(f"Perdu depuis {years[0]}", f"{lost_ha:,.0f} ha".replace(",", " "))
    c3.metric("Surface à risque élevé", f"{high_ha:,.0f} ha".replace(",", " "),
              help="Pixels dont le score de risque dépasse 70 sur 100.")

    st.subheader("Points chauds géolocalisés")
    spots = geo.hotspots(risk)
    if not spots:
        st.info("Aucune cellule au-dessus du seuil critique.")
        return
    df = pd.DataFrame([
        {"Latitude": s["lat"], "Longitude": s["lon"],
         "Risque": s["value"], "Surface (ha)": s["surface_ha"]}
        for s in spots
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Coordonnées réelles, exploitables sur le terrain ou dans un GPS.")
