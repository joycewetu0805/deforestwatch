"""
Notifications e-mail des alertes de déforestation critiques.

Construit un digest (texte + HTML) des alertes actives et l'envoie par SMTP.
Sécurité : l'envoi est **désactivé par défaut** (settings.alert_email_enabled)
et ne part que si le SMTP est configuré dans .env. Sans configuration, la
fonction renvoie l'aperçu sans rien envoyer.
"""

from __future__ import annotations

from config.settings import settings
from src.analysis import alerts as alerts_engine
from src.analysis import carbon
from src.utils.logger import get_logger

log = get_logger("notify")


def build_digest(min_severity: str = "élevée") -> dict:
    """Construit le digest des alertes actives (>= sévérité donnée)."""
    rank = {s: i for i, s in enumerate(alerts_engine.SEVERITIES)}
    threshold = rank.get(min_severity, 1)
    active = [a for a in alerts_engine.active_alerts()
              if rank[a.severity] >= threshold]
    total_co2 = sum(carbon.co2_from_loss(a.area_lost_ha) for a in active)

    subject = f"[DeforestWatch] {len(active)} alerte(s) de déforestation"
    lines = [
        "DeforestWatch-DRC — Alertes de déforestation",
        f"{len(active)} secteur(s) au-dessus du seuil '{min_severity}'.",
        f"CO₂ estimé associé : {total_co2:,.0f} t.",
        "",
    ]
    rows_html = []
    for a in active:
        lines.append(f"  • [{a.severity}] Secteur {a.sector} ({a.year}) — "
                     f"{a.area_lost_ha:,.0f} ha perdus — {a.lat}, {a.lon}")
        rows_html.append(
            f"<tr><td style='padding:4px 10px'>{a.sector}</td>"
            f"<td style='padding:4px 10px'>{a.year}</td>"
            f"<td style='padding:4px 10px;color:#b91c1c'>{a.severity}</td>"
            f"<td style='padding:4px 10px'>{a.area_lost_ha:,.0f} ha</td>"
            f"<td style='padding:4px 10px'>{a.lat}, {a.lon}</td></tr>")

    html = (
        f"<h2 style='color:#0B6E2D'>DeforestWatch-DRC — {len(active)} alerte(s)</h2>"
        f"<p>Seuil : <b>{min_severity}</b> · CO₂ estimé : <b>{total_co2:,.0f} t</b></p>"
        "<table style='border-collapse:collapse;font-family:sans-serif;font-size:14px'>"
        "<tr style='background:#0B6E2D;color:#fff'>"
        "<th style='padding:6px 10px'>Secteur</th><th style='padding:6px 10px'>Année</th>"
        "<th style='padding:6px 10px'>Sévérité</th><th style='padding:6px 10px'>Perte</th>"
        "<th style='padding:6px 10px'>Coordonnées</th></tr>"
        + "".join(rows_html) + "</table>"
    )
    return {
        "subject": subject,
        "text": "\n".join(lines),
        "html": html,
        "count": len(active),
        "co2_t": round(total_co2, 1),
    }


def send_email(digest: dict, to: str | None = None) -> dict:
    """Envoie le digest par SMTP si configuré ; sinon renvoie l'aperçu."""
    recipients = (to or settings.alert_email_to or "").strip()
    if not settings.alert_email_enabled:
        return {"sent": False, "reason": "alert_email_enabled=false (envoi désactivé)",
                "preview": digest}
    if not (settings.smtp_host and settings.alert_email_from and recipients):
        return {"sent": False, "reason": "Configuration SMTP incomplète (.env)",
                "preview": digest}

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["Subject"] = digest["subject"]
    msg["From"] = settings.alert_email_from
    msg["To"] = recipients
    msg.attach(MIMEText(digest["text"], "plain", "utf-8"))
    msg.attach(MIMEText(digest["html"], "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password or "")
            server.sendmail(settings.alert_email_from,
                            [r.strip() for r in recipients.split(",")], msg.as_string())
        log.info(f"Digest envoyé à {recipients} ({digest['count']} alertes).")
        return {"sent": True, "recipients": recipients, "count": digest["count"]}
    except Exception as exc:  # pragma: no cover - dépend du réseau/SMTP
        log.error(f"Échec de l'envoi SMTP : {exc}")
        return {"sent": False, "reason": str(exc), "preview": digest}


def notify_critical(min_severity: str = "élevée", to: str | None = None) -> dict:
    """Construit et (si configuré) envoie le digest des alertes critiques."""
    digest = build_digest(min_severity)
    if digest["count"] == 0:
        return {"sent": False, "reason": "Aucune alerte à notifier", "count": 0}
    return send_email(digest, to)


def main() -> None:
    result = notify_critical()
    log.info(f"Notification : {result.get('reason', 'envoyée')} — "
             f"aperçu : {result.get('preview', {}).get('subject', '')}")


if __name__ == "__main__":
    main()
