"""Tests des endpoints FastAPI : auth, OTP, statistiques, routes admin protégées."""

import pyotp


def test_root_and_health(api_client):
    assert api_client.get("/").status_code == 200
    assert api_client.get("/health").json()["status"] == "ok"


def test_register_and_login_flow(api_client):
    email = "tester@example.cd"
    r = api_client.post("/api/v1/auth/register", json={"email": email, "password": "secret1"})
    assert r.status_code == 200
    assert "otp_provisioning_uri" in r.json()

    # double inscription rejetée
    assert api_client.post("/api/v1/auth/register",
                           json={"email": email, "password": "secret1"}).status_code == 400

    # 2FA imposée : la connexion exige le code OTP (statique en mode démo).
    r = api_client.post("/api/v1/auth/login",
                        json={"email": email, "password": "secret1", "otp_code": "123456"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(api_client):
    api_client.post("/api/v1/auth/register", json={"email": "x@y.cd", "password": "rightpw"})
    r = api_client.post("/api/v1/auth/login",
                        json={"email": "x@y.cd", "password": "wrongpw", "otp_code": "123456"})
    assert r.status_code == 401


def test_login_requires_otp(api_client):
    """Sans code 2FA valide, aucun token n'est émis même avec le bon mot de passe."""
    api_client.post("/api/v1/auth/register", json={"email": "no2fa@y.cd", "password": "secret1"})
    # mot de passe correct mais OTP absent → refus
    assert api_client.post("/api/v1/auth/login",
                           json={"email": "no2fa@y.cd", "password": "secret1"}).status_code == 401
    # OTP erroné → refus
    assert api_client.post("/api/v1/auth/login",
                           json={"email": "no2fa@y.cd", "password": "secret1",
                                 "otp_code": "000000"}).status_code == 401


def test_otp_verification(api_client):
    email = "otp@example.cd"
    r = api_client.post("/api/v1/auth/register", json={"email": email, "password": "secret1"})
    uri = r.json()["otp_provisioning_uri"]
    secret = uri.split("secret=")[1].split("&")[0]
    code = pyotp.TOTP(secret).now()
    r = api_client.post("/api/v1/auth/verify-otp", json={"email": email, "code": code})
    assert r.status_code == 200 and r.json()["verified"] is True


def test_statistics_endpoint(api_client):
    r = api_client.get("/api/v1/statistics")
    assert r.status_code == 200
    assert len(r.json()["statistics"]) == 11


def test_predictions_year_validation(api_client):
    assert api_client.get("/api/v1/predictions/2024").status_code == 200
    assert api_client.get("/api/v1/predictions/1990").status_code == 404


def test_map_landcover_png(api_client):
    r = api_client.get("/api/v1/maps/landcover/2025")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"
    # années différentes => images différentes
    assert api_client.get("/api/v1/maps/landcover/2015").content != r.content
    assert api_client.get("/api/v1/maps/landcover/1999").status_code == 404


def test_map_risk_png(api_client):
    r = api_client.get("/api/v1/maps/risk")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"


def test_admin_requires_auth(api_client):
    assert api_client.get("/api/v1/admin/users").status_code == 401


def test_admin_access_with_admin_token(api_client):
    r = api_client.post("/api/v1/auth/login",
                        json={"email": "admin@deforestwatch.cd", "password": "admin123",
                              "otp_code": "123456"})
    token = r.json()["access_token"]
    r = api_client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_admin_forbidden_for_regular_user(api_client):
    api_client.post("/api/v1/auth/register", json={"email": "reg@user.cd", "password": "secret1"})
    token = api_client.post("/api/v1/auth/login",
                            json={"email": "reg@user.cd", "password": "secret1",
                                  "otp_code": "123456"}).json()["access_token"]
    r = api_client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
