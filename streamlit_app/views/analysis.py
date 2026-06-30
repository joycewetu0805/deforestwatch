"""Page Analyse — exploration par année, comparaison, modèles ML."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import streamlit as st

from config.settings import LAND_COVER_CLASSES, MODELS_DIR, PROCESSED_DIR
from src.data import provider
from src.models.evaluator import confusion
from src.utils.helpers import load_json
from src.visualization import charts, maps
from streamlit_app.components import ui


@st.cache_data(ttl=600)
def _series():
    return provider.landcover_series()


def _class_counts(lc: np.ndarray) -> dict:
    return {c: int(np.sum(lc == c)) for c in LAND_COVER_CLASSES}


def render() -> None:
    ui.header("Analyse exploratoire",
              "Classification de la couverture du sol et comparaison des modèles ML",
              logo="🔬")
    series = _series()
    yrs = sorted(series.keys())

    year = st.slider("Année d'analyse", yrs[0], yrs[-1], yrs[-1])
    lc = series[year]

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader(f"Couverture du sol — {year}")
        st.image(maps.classification_to_rgb(lc), use_column_width=True)
        st.caption(" · ".join(f"{LAND_COVER_CLASSES[c]}" for c in LAND_COVER_CLASSES))
    with c2:
        st.subheader("Répartition des classes")
        st.plotly_chart(charts.class_distribution(_class_counts(lc)), use_container_width=True)

    # ── Comparaison de deux années ──
    st.markdown("---")
    st.subheader("Comparaison de deux années")
    cc1, cc2 = st.columns(2)
    y1 = cc1.selectbox("Année A", yrs, index=0)
    y2 = cc2.selectbox("Année B", yrs, index=len(yrs) - 1)
    ic1, ic2 = st.columns(2)
    ic1.image(maps.classification_to_rgb(series[y1]), caption=str(y1), use_column_width=True)
    ic2.image(maps.classification_to_rgb(series[y2]), caption=str(y2), use_column_width=True)

    # ── Tableau comparatif des modèles ──
    st.markdown("---")
    st.subheader("🏆 Comparaison des modèles ML")
    report_path = Path(PROCESSED_DIR) / "model_metrics.json"
    if report_path.exists():
        report = load_json(report_path)
        st.dataframe(report.get("comparison", []), use_container_width=True, hide_index=True)
        st.success(f"Meilleur modèle : **{report.get('best_model')}**")
    else:
        st.info("Lancez `make train` pour générer les métriques des modèles.")

    # ── Matrice de confusion ──
    st.subheader("Matrice de confusion")
    cm, source_label = _confusion_matrix(lc, year)
    st.caption(source_label)
    st.plotly_chart(charts.confusion_heatmap(cm), use_container_width=True)


def _confusion_matrix(lc, year):
    """Matrice de confusion du Random Forest entraîné si disponible, sinon illustration."""
    model_path = Path(MODELS_DIR) / "random_forest.joblib"
    if model_path.exists():
        try:
            from src.models.random_forest import RandomForestModel

            rf = RandomForestModel.load(model_path)
            bands = provider.composite(year)
            topo = provider.topography()
            pred = rf.predict_image(bands, topo)
            return confusion(lc, pred), "Random Forest entraîné · prédiction sur l'année sélectionnée"
        except Exception:
            pass
    # repli : pseudo-prédiction bruitée (modèle non entraîné)
    pred = lc.copy()
    flip = np.random.default_rng(0).random(lc.shape) < 0.08
    pred[flip] = np.random.default_rng(1).integers(0, 5, int(flip.sum()))
    return confusion(lc, pred), "Illustration (lancez `make train` pour la matrice du modèle réel)"
