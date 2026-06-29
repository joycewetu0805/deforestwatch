"""Composants d'interface réutilisables (thème, en-têtes, cartes KPI)."""

from __future__ import annotations

import streamlit as st

EMERALD = "#10B981"
CYAN = "#06B6D4"
ALERT = "#EF4444"
AMBER = "#F59E0B"
PANEL = "#131A2B"
BASE = "#0A0F1C"


def inject_css() -> None:
    """Style global cohérent avec le frontend React (dark / mission control)."""
    st.markdown(
        f"""
        <style>
          .stApp {{
            background:
              radial-gradient(900px 500px at 12% -8%, rgba(16,185,129,.10), transparent 60%),
              radial-gradient(800px 500px at 110% 0%, rgba(6,182,212,.08), transparent 55%),
              {BASE};
          }}
          #MainMenu, footer {{visibility: hidden;}}
          h1, h2, h3 {{ letter-spacing: -.01em; }}
          h1 {{ color: #F1F5F9 !important; }}
          h2, h3 {{ color: {EMERALD} !important; }}

          /* Cartes KPI maison */
          .dfw-kpi {{
            border: 1px solid rgba(255,255,255,.08);
            background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01));
            border-radius: 16px; padding: 18px 20px; height: 100%;
            transition: border-color .2s, transform .2s;
          }}
          .dfw-kpi:hover {{ border-color: rgba(16,185,129,.45); transform: translateY(-2px); }}
          .dfw-kpi .label {{ color: #94A3B8; font-size: .82rem; }}
          .dfw-kpi .value {{ color: #F8FAFC; font-size: 1.7rem; font-weight: 700; margin-top: 2px; }}
          .dfw-kpi .delta {{ font-size: .8rem; margin-top: 4px; }}

          /* Bandeau d'en-tête */
          .dfw-header {{
            display:flex; align-items:center; gap:14px;
            border:1px solid rgba(255,255,255,.08); border-radius:18px;
            padding:18px 22px; margin-bottom:8px;
            background: linear-gradient(110deg, rgba(16,185,129,.10), rgba(6,182,212,.06));
          }}
          .dfw-header .logo {{ font-size: 2rem; }}
          .dfw-header .title {{ font-size: 1.35rem; font-weight: 800; color:#F1F5F9; }}
          .dfw-header .sub {{ color:#94A3B8; font-size:.85rem; }}

          /* Pastille de statut source */
          .dfw-badge {{ display:inline-block; padding:4px 12px; border-radius:999px;
            font-size:.78rem; font-weight:600; }}
          .dfw-badge.real {{ background:rgba(16,185,129,.18); color:{EMERALD}; }}
          .dfw-badge.demo {{ background:rgba(245,158,11,.16); color:{AMBER}; }}

          section[data-testid="stSidebar"] {{ background: {PANEL}; }}
          div[data-testid="stMetricValue"] {{ color: {CYAN}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def header(title: str, subtitle: str, logo: str = "🌍") -> None:
    st.markdown(
        f"""
        <div class="dfw-header">
          <div class="logo">{logo}</div>
          <div>
            <div class="title">{title}</div>
            <div class="sub">{subtitle}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(col, label: str, value: str, delta: str | None = None, delta_color: str = EMERALD) -> None:
    delta_html = f'<div class="delta" style="color:{delta_color}">{delta}</div>' if delta else ""
    col.markdown(
        f"""
        <div class="dfw-kpi">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_badge(is_real: bool) -> None:
    if is_real:
        st.markdown('<span class="dfw-badge real">🛰️ Données réelles</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="dfw-badge demo">🧪 Données de démonstration</span>',
                    unsafe_allow_html=True)


# Libellés <-> modes internes
_MODE_LABELS = {"Auto": "auto", "Démo (synthétique)": "demo", "Données réelles": "real"}
_LABEL_BY_MODE = {v: k for k, v in _MODE_LABELS.items()}


def data_source_control() -> None:
    """Toggle de la sidebar pour basculer démo ↔ données réelles à chaud."""
    from src.data import provider

    available = provider.has_real_data()
    key = "dfw_data_mode"
    if key not in st.session_state:
        st.session_state[key] = _LABEL_BY_MODE.get(provider.mode(), "Auto")

    st.sidebar.markdown("**🛰️ Source de données**")
    choice = st.sidebar.radio(
        "Source de données", list(_MODE_LABELS.keys()),
        key=key, label_visibility="collapsed",
    )
    chosen = _MODE_LABELS[choice]

    if chosen == "real" and not available:
        st.sidebar.warning("Aucune image dans `data/raw/`. Lancez `make export-demo` "
                           "(GeoTIFF de test) ou déposez vos vraies images.")

    # Applique le changement et vide le cache des données
    if chosen != provider.mode():
        provider.switch(chosen)
        st.cache_data.clear()
        st.rerun()

    effective = "réelle 🛰️" if provider.is_real() else "démo 🧪"
    st.sidebar.caption(f"Active : **{effective}**"
                       + (f" · {len(provider.years())} années" if provider.is_real() else ""))
