"""Graphiques Plotly réutilisables (dashboard + notebooks)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import CLASS_COLORS, LAND_COVER_CLASSES


def forest_evolution(stats: list[dict]):
    """Courbe d'évolution de la surface forestière 2015–2025."""
    import plotly.graph_objects as go

    df = pd.DataFrame(stats)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["total_forest_ha"], mode="lines+markers",
        name="Surface forestière (ha)", line=dict(color="#10B981", width=3),
        fill="tozeroy", fillcolor="rgba(16,185,129,0.15)",
    ))
    fig.update_layout(
        title="Évolution de la couverture forestière (Mai-Ndombe)",
        xaxis_title="Année", yaxis_title="Hectares", template="plotly_dark",
        height=380,
    )
    return fig


def annual_loss_bar(stats: list[dict]):
    import plotly.express as px

    df = pd.DataFrame(stats)
    fig = px.bar(df, x="year", y="forest_loss_ha",
                 title="Perte forestière annuelle (ha)",
                 color="forest_loss_ha", color_continuous_scale="Reds")
    fig.update_layout(template="plotly_dark", height=360, coloraxis_showscale=False)
    return fig


def class_distribution(class_counts: dict):
    import plotly.express as px

    labels = [LAND_COVER_CLASSES[c] for c in sorted(class_counts)]
    values = [class_counts[c] for c in sorted(class_counts)]
    colors = [CLASS_COLORS[c] for c in sorted(class_counts)]
    fig = px.bar(x=labels, y=values, title="Répartition des classes de couverture",
                 color=labels, color_discrete_sequence=colors)
    fig.update_layout(template="plotly_dark", height=360, showlegend=False,
                      xaxis_title="", yaxis_title="Pixels")
    return fig


def confusion_heatmap(cm: np.ndarray, title: str = "Matrice de confusion"):
    import plotly.express as px

    labels = list(LAND_COVER_CLASSES.values())
    fig = px.imshow(cm, x=labels, y=labels, text_auto=True,
                    color_continuous_scale="Blues", title=title)
    fig.update_layout(template="plotly_dark", height=420,
                      xaxis_title="Prédiction", yaxis_title="Réel")
    return fig


def feature_importance_bar(importance: dict, title: str = "Importance des features"):
    import plotly.express as px

    df = pd.DataFrame({"feature": list(importance), "importance": list(importance.values())})
    df = df.sort_values("importance", ascending=True)
    fig = px.bar(df, x="importance", y="feature", orientation="h", title=title)
    fig.update_layout(template="plotly_dark", height=420)
    return fig
