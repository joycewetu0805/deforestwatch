"""Page Admin — gestion utilisateurs, logs, métriques, modèles (role=admin)."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

from streamlit_app.components.auth import DEMO_USERS, current_role


def render() -> None:
    if current_role() != "admin":
        st.error("Accès réservé aux administrateurs.")
        return

    st.title("⚙️ Back-office administrateur")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["👥 Utilisateurs", "📜 Logs", "📈 Métriques d'usage", "🤖 Modèles"]
    )

    # ── Utilisateurs ──
    with tab1:
        st.subheader("Gestion des utilisateurs")
        df = pd.DataFrame([
            {"Email": e, "Rôle": u["role"], "Nom": u["name"], "Actif": True}
            for e, u in DEMO_USERS.items()
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
        with st.form("new_user"):
            col1, col2, col3 = st.columns(3)
            email = col1.text_input("Email")
            role = col2.selectbox("Rôle", ["user", "admin"])
            col3.text_input("Mot de passe temporaire", type="password")
            if st.form_submit_button("Créer l'utilisateur"):
                st.success(f"Utilisateur {email} ({role}) créé (démo).")

    # ── Logs ──
    with tab2:
        st.subheader("Logs d'utilisation de l'API")
        rng = np.random.default_rng(1)
        endpoints = ["/api/v1/statistics", "/api/v1/predictions/2024",
                     "/api/v1/models", "/api/v1/auth/login"]
        logs = pd.DataFrame({
            "Horodatage": [datetime.now() - timedelta(minutes=int(m)) for m in rng.integers(0, 600, 40)],
            "Endpoint": rng.choice(endpoints, 40),
            "Méthode": rng.choice(["GET", "POST"], 40),
            "Statut": rng.choice([200, 200, 200, 401, 404], 40),
        }).sort_values("Horodatage", ascending=False)
        st.dataframe(logs, use_container_width=True, hide_index=True)

    # ── Métriques d'usage ──
    with tab3:
        st.subheader("Trafic API (30 derniers jours)")
        rng = np.random.default_rng(2)
        days = pd.date_range(end=datetime.now(), periods=30)
        usage = pd.DataFrame({"Jour": days, "Requêtes": rng.integers(20, 200, 30)})
        st.bar_chart(usage.set_index("Jour"))
        c1, c2 = st.columns(2)
        c1.metric("Requêtes totales", f"{int(usage['Requêtes'].sum()):,}")
        c2.metric("Utilisateurs actifs", len(DEMO_USERS))

    # ── Modèles ──
    with tab4:
        st.subheader("Modèles déployés")
        from pathlib import Path

        from config.settings import PROCESSED_DIR
        from src.utils.helpers import load_json

        report_path = Path(PROCESSED_DIR) / "model_metrics.json"
        if report_path.exists():
            st.dataframe(load_json(report_path).get("comparison", []),
                         use_container_width=True, hide_index=True)
        else:
            st.info("Aucun modèle entraîné. Lancez `make train`.")
        st.download_button("📄 Générer un rapport (PDF)", data=b"Rapport DeforestWatch-DRC",
                           file_name="rapport_deforestation.txt")
