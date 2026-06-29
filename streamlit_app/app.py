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
from streamlit_app.views import admin, analysis, dashboard, prediction  # noqa: E402

st.set_page_config(
    page_title="DeforestWatch-DRC",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Style sombre cohérent avec le frontend React
st.markdown(
    """
    <style>
      .stApp { background-color: #0A0F1C; }
      h1, h2, h3 { color: #10B981; }
      [data-testid="stMetricValue"] { color: #06B6D4; }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    if not login_form():
        return

    st.sidebar.title("🌍 DeforestWatch-DRC")
    st.sidebar.caption(f"Connecté : {st.session_state.get('user_name')} "
                       f"({st.session_state.get('user_role')})")

    pages = {
        "📊 Dashboard": dashboard.render,
        "🔬 Analyse": analysis.render,
        "🔮 Prédictions": prediction.render,
    }
    if current_role() == "admin":
        pages["⚙️ Admin"] = admin.render

    choice = st.sidebar.radio("Navigation", list(pages.keys()))
    logout_button()
    st.sidebar.markdown("---")
    st.sidebar.caption("Sentinel-2/ESA · Landsat/NASA · UPC FASI · 2026")

    pages[choice]()


if __name__ == "__main__":
    main()
