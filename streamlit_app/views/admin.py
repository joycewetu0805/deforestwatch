"""Page Admin — gestion utilisateurs, logs, métriques, modèles (role=admin)."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

from streamlit_app.components.auth import DEMO_USERS, current_role
from streamlit_app.components import ui


def render() -> None:
    if current_role() != "admin":
        st.error("Accès réservé aux administrateurs.")
        return

    ui.header("Back-office administrateur",
              "Utilisateurs · journaux d'API · métriques d'usage · modèles déployés",
              logo="⚙️")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["👥 Utilisateurs", "📜 Logs", "📈 Métriques d'usage", "🤖 Modèles", "📧 Notifications"]
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

    # ── Notifications e-mail ──
    with tab5:
        st.subheader("Notifier les alertes par e-mail")
        from src.analysis import notify
        from config.settings import settings as cfg

        sev = st.selectbox("Sévérité minimale", ["critique", "élevée", "modérée"], index=1)
        digest = notify.build_digest(sev)
        st.metric("Alertes à notifier", digest["count"])
        st.metric("CO₂ associé", f"{digest['co2_t']:,.0f} t")
        with st.expander("Aperçu de l'e-mail"):
            st.text(digest["text"])
        if cfg.alert_email_enabled:
            st.success("Envoi SMTP activé.")
        else:
            st.warning("Envoi désactivé (ALERT_EMAIL_ENABLED=false). Configurez le SMTP "
                       "dans `.env` pour envoyer réellement.")
        if st.button("📧 Envoyer le digest maintenant", type="primary"):
            res = notify.notify_critical(sev)
            if res.get("sent"):
                st.success(f"✅ Envoyé à {res['recipients']} ({res['count']} alertes).")
            else:
                st.info(f"Non envoyé : {res.get('reason')} (aperçu généré ci-dessus).")
