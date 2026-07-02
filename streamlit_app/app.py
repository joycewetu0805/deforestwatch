"""
Dashboard Streamlit DeforestWatch-DRC — point d'entrée.
Connexion 2FA puis navigation multi-pages (Dashboard, Analyse, Prédictions, Admin).

Lancement : streamlit run streamlit_app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permet d'importer le package src depuis la racine du projet
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from streamlit_app.components.auth import current_role, login_form, logout_button  # noqa: E402
from streamlit_app.components import ui  # noqa: E402
from streamlit_app.views import admin, alerts, analysis, dashboard, prediction  # noqa: E402

st.set_page_config(
    page_title="DeforestWatch-DRC",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    if not login_form():
        return

    ui.inject_css()
    st.sidebar.markdown(
        "<div style='font-size:1.3rem;font-weight:800;color:#10B981;'>🌍 DeforestWatch</div>"
        "<div style='color:#94A3B8;font-size:.8rem;margin-bottom:8px;'>RDC · Mai-Ndombe</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption(f"👤 {st.session_state.get('user_name')} · "
                       f"{st.session_state.get('user_role')}")

    pages = {
        "📊 Dashboard": dashboard.render,
        "🚨 Alertes": alerts.render,
        "🔬 Analyse": analysis.render,
        "🔮 Prédictions": prediction.render,
    }
    if current_role() == "admin":
        pages["⚙️ Admin"] = admin.render

    choice = st.sidebar.radio("Navigation", list(pages.keys()))
    st.sidebar.markdown("---")
    ui.data_source_control()
    st.sidebar.markdown("---")
    logout_button()
    st.sidebar.caption("Sentinel-2/ESA · Landsat/NASA · UPC FASI · 2026")

    pages[choice]()


if __name__ == "__main__":
    main()
