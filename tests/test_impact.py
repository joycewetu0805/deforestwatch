"""Tests : estimation carbone, radar Sentinel-1, notifications e-mail."""

import numpy as np

from src.analysis import carbon, notify
from src.data import radar


# ── Carbone ──
def test_co2_from_loss_positive():
    from config.settings import CO2_TONNES_PER_HA

    assert carbon.co2_from_loss(100) == round(100 * CO2_TONNES_PER_HA, 1)
    assert carbon.co2_from_loss(-5) == 0.0


def test_yearly_carbon_cumulative_monotonic():
    yc = carbon.yearly_carbon()
    cum = [y["co2_cumulative_t"] for y in yc]
    assert cum == sorted(cum)  # cumulatif croissant
    assert len(yc) >= 2


def test_carbon_summary_keys():
    s = carbon.summary()
    for k in ["total_co2_t", "total_co2_mt", "equivalents", "assumptions", "worst_year"]:
        assert k in s
    assert s["equivalents"]["cars_year"] > 0


# ── Radar ──
def test_radar_composite_shape_and_units():
    lc = np.zeros((32, 32), dtype=np.int8)
    r = radar.landcover_to_radar(lc)
    assert r.shape == (32, 32, 2)
    assert r.mean() < 0            # dB négatifs


def test_rvi_forest_gt_bare():
    forest = radar.landcover_to_radar(np.zeros((16, 16), dtype=np.int8))
    bare = radar.landcover_to_radar(np.full((16, 16), 2, dtype=np.int8))
    assert radar.radar_vegetation_index(forest).mean() > radar.radar_vegetation_index(bare).mean()


def test_cloud_penetration_gain():
    demo = radar.cloud_penetration_demo(2025, cloud_fraction=0.5)
    assert demo["radar_usable_pct"] == 100.0
    assert demo["gain_pct"] > 0


# ── Notifications ──
def test_build_digest_structure():
    d = notify.build_digest("modérée")
    for k in ["subject", "text", "html", "count", "co2_t"]:
        assert k in d
    assert "DeforestWatch" in d["subject"]


def test_notify_disabled_by_default():
    res = notify.notify_critical("élevée")
    # envoi désactivé -> pas d'envoi, aperçu fourni
    assert res["sent"] is False


def test_carbon_endpoint(api_client):
    r = api_client.get("/api/v1/carbon")
    assert r.status_code == 200
    assert "summary" in r.json() and "yearly" in r.json()


def test_radar_coverage_endpoint(api_client):
    assert api_client.get("/api/v1/radar/coverage/2025").status_code == 200
    assert api_client.get("/api/v1/radar/coverage/1999").status_code == 404


def test_notify_endpoint_admin_only(api_client):
    assert api_client.post("/api/v1/admin/notify").status_code == 401
    tok = api_client.post("/api/v1/auth/login", json={
        "email": "admin@deforestwatch.cd", "password": "admin123",
        "otp_code": "123456"}).json()["access_token"]
    r = api_client.post("/api/v1/admin/notify", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
