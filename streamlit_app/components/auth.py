"""Composant d'authentification du dashboard Streamlit."""

from __future__ import annotations

import streamlit as st


# Comptes de démo (en production : appel à l'API /auth/login + OTP)
DEMO_USERS = {
    "admin@deforestwatch.cd": {"password": "admin123", "role": "admin", "name": "Administrateur"},
    "user@deforestwatch.cd": {"password": "user123", "role": "user", "name": "Analyste"},
}
DEMO_OTP = "123456"  # code 2FA fixe en mode démo


def login_form() -> bool:
    """Affiche le formulaire de connexion. Renvoie True si authentifié."""
    if st.session_state.get("authenticated"):
        return True

    st.markdown("## 🔐 Connexion — DeforestWatch-DRC")
    st.caption("Démo : admin@deforestwatch.cd / admin123 — code 2FA : 123456")

    with st.form("login"):
        email = st.text_input("Email", value="admin@deforestwatch.cd")
        password = st.text_input("Mot de passe", type="password")
        otp = st.text_input("Code 2FA (Google Authenticator)", max_chars=6)
        submitted = st.form_submit_button("Se connecter", use_container_width=True)

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
