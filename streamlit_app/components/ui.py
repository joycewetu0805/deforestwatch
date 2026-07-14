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


def inject_landing_css() -> None:
    """Style de la page d'accueil (avant connexion) : landing « AI data app »
    (thème sombre, dégradé spectral émeraude→cyan→violet, animations CSS pures).
    """
    st.markdown(
        """
        <style>
          :root {
            --a1:#23C98C; --a2:#35C9E6; --a3:#7A6CF2;
            --ink:#EAF0FB; --muted:#99A6BF; --muted2:#6B7891;
            --line:rgba(255,255,255,.09); --line2:rgba(255,255,255,.14);
            --surface:#101726; --surface2:#141D30; --bg2:#0C111C;
            --grad:linear-gradient(100deg,var(--a1),var(--a2) 46%,var(--a3));
          }
          /* Plein écran, on masque le chrome Streamlit sur la landing */
          header[data-testid="stHeader"], #MainMenu, footer {display:none;}
          section[data-testid="stSidebar"] {display:none;}
          .stApp {
            background:
              radial-gradient(60% 55% at 16% -6%, rgba(35,201,140,.16), transparent 70%),
              radial-gradient(55% 55% at 82% 2%, rgba(122,108,242,.20), transparent 70%),
              #070A11;
          }
          .block-container {padding-top:2.2rem; padding-bottom:0; max-width:1180px;}

          .dfw-land h1,.dfw-land h2,.dfw-land h3{margin:0;letter-spacing:-.02em;line-height:1.05;color:var(--ink)!important;}
          .dfw-grad{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;}
          .dfw-eyebrow{display:inline-flex;align-items:center;gap:9px;font-size:12px;letter-spacing:.14em;
            text-transform:uppercase;color:var(--muted);font-weight:600;padding:7px 14px;border:1px solid var(--line);
            border-radius:100px;background:rgba(255,255,255,.02);}
          .dfw-eyebrow .dot{width:7px;height:7px;border-radius:50%;background:var(--a1);
            box-shadow:0 0 0 4px rgba(35,201,140,.18);animation:dfwpulse 2.4s ease-in-out infinite;}
          @keyframes dfwpulse{50%{box-shadow:0 0 0 8px rgba(35,201,140,0);}}
          .dfw-h1{font-size:clamp(34px,5vw,58px);font-weight:800;margin-top:20px!important;}
          .dfw-sub{margin-top:18px;font-size:18px;color:var(--muted);max-width:36ch;}
          .dfw-meta{margin-top:22px;display:flex;gap:20px;color:var(--muted2);font-size:13px;flex-wrap:wrap;}
          .dfw-meta b{color:var(--ink);font-weight:600;}

          /* Carte data-app / graphique */
          .dfw-card{background:linear-gradient(180deg,var(--surface),var(--bg2));border:1px solid var(--line2);
            border-radius:16px;box-shadow:0 24px 60px -20px rgba(0,0,0,.7);overflow:hidden;}
          .dfw-card .bar{display:flex;align-items:center;gap:8px;padding:12px 15px;border-bottom:1px solid var(--line);}
          .dfw-card .bar .d{width:10px;height:10px;border-radius:50%;background:#2a3550;}
          .dfw-card .bar .tt{margin-left:6px;font-size:12px;color:var(--muted);font-family:ui-monospace,Menlo,monospace;}
          .dfw-card .bar .live{margin-left:auto;font-size:10.5px;color:var(--a1);letter-spacing:.08em;display:flex;align-items:center;gap:6px;}
          .dfw-card .bar .live::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--a1);box-shadow:0 0 8px var(--a1);}
          .dfw-body{padding:15px;}
          .dfw-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:12px;}
          .dfw-k{background:var(--surface2);border:1px solid var(--line);border-radius:10px;padding:10px 12px;}
          .dfw-k .v{font-size:19px;font-weight:700;font-variant-numeric:tabular-nums;}
          .dfw-k .v.down{color:#F26B45;}
          .dfw-k .l{font-size:10.5px;color:var(--muted2);margin-top:2px;}
          .dfw-chart{background:var(--surface2);border:1px solid var(--line);border-radius:11px;padding:11px;}
          .dfw-chart .hd{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:2px;}
          .dfw-chart .hd .n{color:var(--a2);font-variant-numeric:tabular-nums;}
          .dfw-chart svg{width:100%;height:auto;display:block;}
          .dfw-spark{fill:none;stroke:url(#dfwg);stroke-width:2.5;stroke-linecap:round;
            stroke-dasharray:1200;stroke-dashoffset:1200;animation:dfwdraw 2s ease-out .3s forwards;}
          @keyframes dfwdraw{to{stroke-dashoffset:0;}}
          .dfw-legend{display:flex;gap:12px;margin-top:9px;flex-wrap:wrap;}
          .dfw-legend span{font-size:10.5px;color:var(--muted);display:inline-flex;align-items:center;gap:5px;}
          .dfw-legend i{width:9px;height:9px;border-radius:3px;}

          /* Bandeau de stats */
          .dfw-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;border-top:1px solid var(--line);
            border-bottom:1px solid var(--line);padding:30px 0;margin:8px 0;}
          .dfw-stat .v{font-size:clamp(24px,3.2vw,34px);font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.02em;}
          .dfw-stat .l{color:var(--muted);font-size:13px;margin-top:3px;}

          /* Grille de features */
          .dfw-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
          .dfw-feat{background:linear-gradient(180deg,var(--surface),var(--bg2));border:1px solid var(--line);
            border-radius:15px;padding:22px 20px;transition:transform .2s,border-color .2s;}
          .dfw-feat:hover{transform:translateY(-4px);border-color:var(--line2);}
          .dfw-feat .ico{width:40px;height:40px;border-radius:11px;display:grid;place-items:center;
            background:rgba(53,201,230,.10);border:1px solid rgba(53,201,230,.22);margin-bottom:14px;font-size:19px;}
          .dfw-feat h3{font-size:17px;font-weight:700;}
          .dfw-feat p{margin:8px 0 0;color:var(--muted);font-size:13.5px;line-height:1.55;}

          /* Barres de modèles */
          .dfw-models{background:linear-gradient(180deg,var(--surface),var(--bg2));border:1px solid var(--line);
            border-radius:15px;padding:22px;}
          .dfw-mbar{margin-bottom:14px;}
          .dfw-mbar .top{display:flex;justify-content:space-between;font-size:13.5px;margin-bottom:6px;color:var(--ink);}
          .dfw-mbar .top b{font-variant-numeric:tabular-nums;}
          .dfw-track{height:9px;border-radius:6px;background:var(--surface2);border:1px solid var(--line);overflow:hidden;}
          .dfw-fill{height:100%;border-radius:6px;background:var(--grad);transform-origin:left;transform:scaleX(0);
            animation:dfwgrow 1.2s cubic-bezier(.2,.7,.2,1) .3s forwards;}
          @keyframes dfwgrow{to{transform:scaleX(1);}}

          .dfw-sechead{max-width:640px;margin:6px 0 26px;}
          .dfw-sechead h2{font-size:clamp(26px,3.6vw,38px);font-weight:800;margin-top:14px!important;}
          .dfw-sechead p{margin-top:12px;color:var(--muted);font-size:16px;}

          /* Entrée en fondu */
          .dfw-up{animation:dfwup .7s both;}
          @keyframes dfwup{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:none;}}

          /* Formulaire de connexion Streamlit stylé en carte */
          div[data-testid="stForm"]{background:linear-gradient(180deg,var(--surface),var(--bg2));
            border:1px solid var(--line2)!important;border-radius:16px;padding:22px 22px 8px;
            box-shadow:0 24px 60px -20px rgba(0,0,0,.7);position:relative;}
          div[data-testid="stForm"]::before{content:"";position:absolute;inset:0 0 auto 0;height:3px;
            background:var(--grad);border-radius:16px 16px 0 0;}
          div[data-testid="stForm"] label{color:var(--muted)!important;font-size:13px!important;}
          div[data-testid="stForm"] input{background:#0A0F1A!important;color:var(--ink)!important;
            border:1px solid var(--line)!important;}
          div[data-testid="stFormSubmitButton"] button{background:var(--grad)!important;color:#06110C!important;
            border:none!important;font-weight:700!important;box-shadow:0 10px 30px -8px rgba(53,201,230,.5);}
          div[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-1px);}

          @media (max-width:820px){.dfw-strip{grid-template-columns:repeat(2,1fr);gap:22px 14px;}
            .dfw-grid{grid-template-columns:1fr;}}
          @media (prefers-reduced-motion:reduce){
            *{animation:none!important;}.dfw-spark{stroke-dashoffset:0;}.dfw-fill{transform:none;}}
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
