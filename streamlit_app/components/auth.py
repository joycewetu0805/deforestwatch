"""Composant d'authentification du dashboard Streamlit."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components import ui

# Comptes de démo (en production : appel à l'API /auth/login + OTP)
DEMO_USERS = {
    "admin@deforestwatch.cd": {"password": "admin123", "role": "admin", "name": "Administrateur"},
    "user@deforestwatch.cd": {"password": "user123", "role": "user", "name": "Analyste"},
}
DEMO_OTP = "123456"  # code 2FA fixe en mode démo


def login_form() -> bool:
    """Landing page « AI data app » + connexion 2FA. Renvoie True si authentifié."""
    if st.session_state.get("authenticated"):
        return True

    ui.inject_landing_css()

    # ── HERO : texte + carte de connexion ────────────────────────────────
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown(
            '<div class="dfw-land dfw-up">'
            '<span class="dfw-eyebrow"><span class="dot"></span>'
            'Data app · Télédétection + Machine Learning</span>'
            '<h1 class="dfw-h1">De l\'image satellite à la '
            '<span class="dfw-grad">décision</span> pour la forêt équatoriale.</h1>'
            '<p class="dfw-sub">DeforestWatch-DRC détecte, quantifie et anticipe la '
            'déforestation du Bassin du Congo — du pixel Sentinel-2 au tableau de bord.</p>'
            '<div class="dfw-meta"><span><b>Sentinel-2</b> · 10 m</span>'
            '<span><b>Mai-Ndombe</b> · RDC</span><span><b>2017–2025</b></span></div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            '<div class="dfw-land dfw-up" style="margin-bottom:-6px;">'
            '<div style="display:flex;align-items:center;gap:8px;font-size:13px;'
            'color:var(--muted);font-weight:600;">🔐 Connexion sécurisée'
            '<span style="margin-left:auto;font-size:10.5px;letter-spacing:.08em;'
            'color:var(--a1);">● EN DIRECT</span></div></div>',
            unsafe_allow_html=True,
        )
        with st.form("login"):
            email = st.text_input("Email", value="admin@deforestwatch.cd")
            password = st.text_input("Mot de passe", type="password",
                                     placeholder="admin123")
            otp = st.text_input("Code 2FA (Google Authenticator)", max_chars=6,
                                placeholder="123456")
            submitted = st.form_submit_button("Lancer la démo →",
                                              use_container_width=True, type="primary")
        st.caption("Démo — admin@deforestwatch.cd / admin123 · 2FA : 123456")

    # ── Bandeau de statistiques ──────────────────────────────────────────
    st.markdown(
        '<div class="dfw-land dfw-up"><div class="dfw-strip">'
        '<div class="dfw-stat"><div class="v dfw-grad">250 000</div>'
        '<div class="l">Hectares surveillés (Mai-Ndombe)</div></div>'
        '<div class="dfw-stat"><div class="v">9</div>'
        '<div class="l">Années d\'archives (2017–2025)</div></div>'
        '<div class="dfw-stat"><div class="v">5</div>'
        '<div class="l">Classes de couverture du sol</div></div>'
        '<div class="dfw-stat"><div class="v dfw-grad">0,90</div>'
        '<div class="l">F1-score du meilleur modèle</div></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # ── Split : graphique data-app + extrait de code ─────────────────────
    st.markdown(
        '<div class="dfw-land dfw-up" style="margin-top:34px;">'
        '<div class="dfw-sechead"><span class="dfw-eyebrow">Du pixel à la décision</span>'
        '<h2>Écrit en Python. <span class="dfw-grad">Servi comme une app.</span></h2>'
        '<p>Collecte, indices spectraux, classification et impact carbone — '
        'toute la chaîne, en direct.</p></div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start;">'
        # carte data-app avec graphique
        '<div class="dfw-card"><div class="bar"><span class="d"></span><span class="d"></span>'
        '<span class="d"></span><span class="tt">deforestwatch — dashboard</span>'
        '<span class="live">EN DIRECT</span></div><div class="dfw-body">'
        '<div class="dfw-kpis">'
        '<div class="dfw-k"><div class="v">46 040</div><div class="l">ha · 2025</div></div>'
        '<div class="dfw-k"><div class="v down">−79 %</div><div class="l">depuis 2015</div></div>'
        '<div class="dfw-k"><div class="v">95,6</div><div class="l">Mt CO₂</div></div></div>'
        '<div class="dfw-chart"><div class="hd"><span>Couverture forestière (kha)</span>'
        '<span class="n">2015 → 2025</span></div>'
        '<svg viewBox="0 0 600 250" role="img" aria-label="Déclin forestier 2015-2025">'
        '<defs><linearGradient id="dfwg" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#23C98C"/><stop offset=".5" stop-color="#35C9E6"/>'
        '<stop offset="1" stop-color="#7A6CF2"/></linearGradient>'
        '<linearGradient id="dfwf" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="rgba(53,201,230,.28)"/>'
        '<stop offset="1" stop-color="rgba(53,201,230,0)"/></linearGradient></defs>'
        '<g stroke="rgba(255,255,255,.05)"><line x1="40" y1="60" x2="560" y2="60"/>'
        '<line x1="40" y1="130" x2="560" y2="130"/><line x1="40" y1="200" x2="560" y2="200"/></g>'
        '<path d="M40,40 L92,52 L144,67 L196,86 L248,107 L300,128 L352,150 L404,170 '
        'L456,189 L508,206 L560,220 L560,230 L40,230 Z" fill="url(#dfwf)"/>'
        '<path class="dfw-spark" d="M40,40 L92,52 L144,67 L196,86 L248,107 L300,128 '
        'L352,150 L404,170 L456,189 L508,206 L560,220"/>'
        '<circle cx="560" cy="220" r="4.5" fill="#7A6CF2"/></svg>'
        '<div class="dfw-legend"><span><i style="background:#23C98C"></i>Forêt dense</span>'
        '<span><i style="background:#9BCC4F"></i>Dégradée</span>'
        '<span><i style="background:#D9A441"></i>Agriculture</span>'
        '<span><i style="background:#F26B45"></i>Perte</span></div></div></div></div>'
        # panneau modèles
        '<div class="dfw-models"><h3 style="font-size:16px;font-weight:700;margin-bottom:14px;">'
        'Comparaison des modèles · F1-macro</h3>'
        '<div class="dfw-mbar"><div class="top"><span>XGBoost</span><b>0,90</b></div>'
        '<div class="dfw-track"><div class="dfw-fill" style="width:90%"></div></div></div>'
        '<div class="dfw-mbar"><div class="top"><span>Random Forest</span><b>0,89</b></div>'
        '<div class="dfw-track"><div class="dfw-fill" style="width:89%"></div></div></div>'
        '<div class="dfw-mbar"><div class="top"><span>U-Net (CNN)</span><b>0,89</b></div>'
        '<div class="dfw-track"><div class="dfw-fill" style="width:89%"></div></div></div>'
        '<h3 style="font-size:15px;font-weight:700;margin:18px 0 10px;">5 classes cartographiées</h3>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;font-size:12.5px;color:var(--muted);">'
        '<span><i style="display:inline-block;width:11px;height:11px;border-radius:3px;background:#23C98C;margin-right:6px;"></i>Forêt dense</span>'
        '<span><i style="display:inline-block;width:11px;height:11px;border-radius:3px;background:#9BCC4F;margin-right:6px;"></i>Forêt dégradée</span>'
        '<span><i style="display:inline-block;width:11px;height:11px;border-radius:3px;background:#D9A441;margin-right:6px;"></i>Agriculture</span>'
        '<span><i style="display:inline-block;width:11px;height:11px;border-radius:3px;background:#35C9E6;margin-right:6px;"></i>Eau</span>'
        '<span><i style="display:inline-block;width:11px;height:11px;border-radius:3px;background:#F26B45;margin-right:6px;"></i>Bâti</span>'
        '</div></div></div></div>',
        unsafe_allow_html=True,
    )

    # ── Grille de fonctionnalités ────────────────────────────────────────
    st.markdown(
        '<div class="dfw-land dfw-up" style="margin-top:40px;">'
        '<div class="dfw-sechead"><span class="dfw-eyebrow">Une plateforme, pas un simple constat</span>'
        '<h2>Tout ce qu\'il faut pour <span class="dfw-grad">agir</span>.</h2></div>'
        '<div class="dfw-grid">'
        '<div class="dfw-feat"><div class="ico">🛰️</div><h3>Détection par IA</h3>'
        '<p>Classification des images Sentinel-2 en 5 classes via NDVI, EVI, NBR et topographie.</p></div>'
        '<div class="dfw-feat"><div class="ico">🔮</div><h3>Carte de risque prédictive</h3>'
        '<p>Anticipe les fronts de déforestation selon la proximité aux routes, villages et coupes.</p></div>'
        '<div class="dfw-feat"><div class="ico">🌱</div><h3>Impact carbone (REDD+)</h3>'
        '<p>Chaque hectare perdu traduit en tonnes de CO₂ — le langage de la finance climat.</p></div>'
        '<div class="dfw-feat"><div class="ico">📍</div><h3>Alertes géolocalisées</h3>'
        '<p>Détection automatique par secteur pour intervenir vite sur une coupe en cours.</p></div>'
        '<div class="dfw-feat"><div class="ico">📡</div><h3>Radar Sentinel-1</h3>'
        '<p>La surveillance passe même à travers les nuages persistants de la zone équatoriale.</p></div>'
        '<div class="dfw-feat"><div class="ico">💬</div><h3>Signalement citoyen</h3>'
        '<p>Les communautés locales remontent l\'information terrain dans la plateforme.</p></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # ── Bandeau final + pied de page ─────────────────────────────────────
    st.markdown(
        '<div class="dfw-land dfw-up" style="margin-top:44px;text-align:center;'
        'border:1px solid var(--line2);border-radius:22px;padding:52px 28px;'
        'background:radial-gradient(120% 160% at 50% 0%, rgba(122,108,242,.20), transparent 60%), var(--surface);">'
        '<h2 style="font-size:clamp(26px,4vw,40px);font-weight:800;">'
        'Protéger la deuxième forêt tropicale <span class="dfw-grad">du monde.</span></h2>'
        '<p style="margin:14px auto 0;color:var(--muted);max-width:46ch;font-size:16px;">'
        'Un outil conçu et maîtrisé localement, au service de la souveraineté '
        'environnementale de la RDC. Connectez-vous ci-dessus pour lancer la démo.</p></div>'
        '<div class="dfw-land" style="margin:26px 0 8px;display:flex;justify-content:space-between;'
        'flex-wrap:wrap;gap:10px;color:var(--muted2);font-size:12.5px;border-top:1px solid var(--line);padding-top:18px;">'
        '<span>© 2026 DeforestWatch-DRC · Joyce A. WETUNGANI · UPC / FASI</span>'
        '<span>Données : ESA Copernicus · NASA/USGS · Google Dynamic World</span></div>',
        unsafe_allow_html=True,
    )

    # ── Validation ───────────────────────────────────────────────────────
    if submitted:
        user = DEMO_USERS.get(email)
        if not user or user["password"] != password:
            st.error("Identifiants invalides.")
            return False
        if otp != DEMO_OTP:
            st.error("Code 2FA invalide.")
            return False
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = email
        st.session_state["user_role"] = user["role"]
        st.session_state["user_name"] = user["name"]
        st.rerun()
    return False


def logout_button() -> None:
    if st.sidebar.button("Se déconnecter", use_container_width=True):
        for k in ["authenticated", "user_email", "user_role", "user_name"]:
            st.session_state.pop(k, None)
        st.rerun()


def current_role() -> str:
    return st.session_state.get("user_role", "user")
