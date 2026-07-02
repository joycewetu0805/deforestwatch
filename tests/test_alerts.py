"""Tests de la détection d'alertes et des endpoints alertes / signalements."""

from src.analysis import alerts as ae


def test_detect_alerts_structure():
    alerts = ae.detect_alerts()
    assert isinstance(alerts, list) and len(alerts) > 0
    a = alerts[0]
    assert a.severity in ae.SEVERITIES
    assert a.area_lost_ha > 0
    assert -90 <= a.lat <= 90 and -180 <= a.lon <= 180


def test_threshold_reduces_alerts():
    many = ae.detect_alerts(threshold_ha=200)
    few = ae.detect_alerts(threshold_ha=1000)
    assert len(few) <= len(many)


def test_summary_keys():
    s = ae.summary()
    for k in ["total_alerts", "by_severity", "total_area_lost_ha", "active_alerts"]:
        assert k in s
    assert sum(s["by_severity"].values()) == s["total_alerts"]


def test_active_alerts_are_latest_year():
    active = ae.active_alerts()
    if active:
        assert len({a.year for a in active}) == 1


def test_alerts_endpoint(api_client):
    r = api_client.get("/api/v1/alerts?limit=5")
    assert r.status_code == 200
    assert len(r.json()) <= 5
    assert api_client.get("/api/v1/alerts/summary").status_code == 200


def test_report_submission_flow(api_client):
    r = api_client.post("/api/v1/reports", json={
        "lat": -1.95, "lon": 18.27, "description": "Coupe suspecte observée",
        "reporter": "citoyen@test.cd"})
    assert r.status_code == 200
    assert r.json()["status"] == "nouveau"
    # validation : latitude hors bornes rejetée
    assert api_client.post("/api/v1/reports", json={
        "lat": 999, "lon": 0, "description": "x"}).status_code == 422


def test_admin_reports_protected(api_client):
    assert api_client.get("/api/v1/admin/reports").status_code == 401
    tok = api_client.post("/api/v1/auth/login", json={
        "email": "admin@deforestwatch.cd", "password": "admin123"}).json()["access_token"]
    r = api_client.get("/api/v1/admin/reports", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
