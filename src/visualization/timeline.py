"""Évolution temporelle annotée de la déforestation."""

from __future__ import annotations

import pandas as pd


def deforestation_timeline(stats: list[dict]):
    """Timeline cumulée de la perte forestière avec annotations d'événements."""
    import plotly.graph_objects as go

    df = pd.DataFrame(stats)
    df["cumulative_loss"] = df["forest_loss_ha"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["cumulative_loss"], mode="lines+markers",
        name="Perte cumulée (ha)", line=dict(color="#EF4444", width=3),
    ))
    # annotation du pic de perte
    if len(df) > 1:
        peak = df.loc[df["forest_loss_ha"].idxmax()]
        fig.add_annotation(x=peak["year"], y=df.loc[peak.name, "cumulative_loss"],
                           text=f"Pic : {peak['forest_loss_ha']:.0f} ha",
                           showarrow=True, arrowhead=2, font=dict(color="#EF4444"))
    fig.update_layout(title="Déforestation cumulée 2015–2025",
                      xaxis_title="Année", yaxis_title="Hectares cumulés",
                      template="plotly_dark", height=380)
    return fig
