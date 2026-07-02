"""Endpoints RESTful de l'API DeforestWatch-DRC."""

from __future__ import annotations

import io
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from config.settings import ANALYSIS_YEARS, settings
from src.api import auth
from src.api.database import User, get_db
from src.api.schemas import (
    OTPVerify, RegisterResponse, TokenResponse, UserLogin, UserOut, UserRegister,
)
from src.utils.helpers import load_json
from src.data import provider
from src.visualization import maps

router = APIRouter(prefix="/api/v1")


def _png(rgb, size: int = 512) -> bytes:
    """Encode un tableau RGB (H,W,3) en PNG agrandi (rendu net, plus proche voisin)."""
    from PIL import Image

    img = Image.fromarray(rgb).resize((size, size), Image.NEAREST)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Authentification ──
@router.post("/auth/register", response_model=RegisterResponse, tags=["auth"])
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email déjà enregistré")
    secret = auth.generate_otp_secret()
    user = User(
        email=payload.email,
        password_hash=auth.hash_password(payload.password),
        otp_secret=secret,
        role="user",
    )
    db.add(user)
    db.commit()
    return RegisterResponse(
        email=user.email,
        otp_provisioning_uri=auth.otp_provisioning_uri(secret, user.email),
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    return TokenResponse(
        access_token=auth.create_access_token(user.email, user.role),
        refresh_token=auth.create_refresh_token(user.email),
    )


@router.post("/auth/verify-otp", tags=["auth"])
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not auth.verify_otp(user.otp_secret, payload.code):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Code OTP invalide")
    return {"verified": True, "message": "2FA validée"}


@router.post("/auth/refresh", response_model=TokenResponse, tags=["auth"])
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    payload = auth.decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token de rafraîchissement invalide")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable")
    return TokenResponse(
        access_token=auth.create_access_token(user.email, user.role),
        refresh_token=auth.create_refresh_token(user.email),
    )


# ── Données de déforestation (publiques) ──
@router.get("/statistics", tags=["data"])
def statistics():
    """Statistiques de déforestation par année (source active : démo ou réelle)."""
    return {
        "study_area": "Mai-Ndombe — forêt équatoriale du Bassin du Congo",
        "data_source": provider.source_name(),
        "is_real_data": provider.is_real(),
        "statistics": provider.yearly_statistics(),
    }


@router.get("/source", tags=["data"])
def data_source():
    """Métadonnées de la source de données active (démo synthétique ou réelle)."""
    return provider.info()


@router.get("/maps/landcover/{year}", tags=["maps"],
            responses={200: {"content": {"image/png": {}}}})
def map_landcover(year: int):
    """Carte de couverture du sol (classification) d'une année, en PNG."""
    series = provider.landcover_series()
    if year not in series:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            f"Année {year} indisponible.")
    rgb = maps.classification_to_rgb(series[year])
    return Response(_png(rgb), media_type="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})


@router.get("/maps/risk", tags=["maps"],
            responses={200: {"content": {"image/png": {}}}})
def map_risk():
    """Carte de risque de déforestation, en PNG (dégradé vert→rouge)."""
    rgb = maps.risk_to_rgb(provider.risk_map())
    return Response(_png(rgb), media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})


@router.post("/admin/source/{mode}", tags=["admin"])
def switch_source(mode: str, _: User = Depends(auth.require_role("admin"))):
    """Bascule la source de données à chaud : mode ∈ {auto, demo, real} (admin)."""
    if mode not in ("auto", "demo", "real"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Mode invalide (attendu : auto, demo, real).")
    provider.switch(mode)
    return provider.info()


@router.get("/predictions/{year}", tags=["data"])
def predictions(year: int):
    """Synthèse de la carte de risque pour une année (zones critiques)."""
    if year not in ANALYSIS_YEARS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Année hors période {ANALYSIS_YEARS[0]}–{ANALYSIS_YEARS[-1]}")
    import numpy as np

    rmap = provider.risk_map()
    high = int(np.sum(rmap > 70))
    return {
        "year": year,
        "high_risk_pixels": high,
        "high_risk_ha": round(high * 0.038, 1),
        "mean_risk": round(float(rmap[rmap > 0].mean()), 1) if (rmap > 0).any() else 0.0,
        "grid_shape": list(rmap.shape),
    }


@router.get("/models", tags=["data"])
def models():
    """Liste des modèles avec leurs performances (depuis le rapport d'entraînement)."""
    from config.settings import PROCESSED_DIR

    report_path = Path(PROCESSED_DIR) / "model_metrics.json"
    if report_path.exists():
        report = load_json(report_path)
        return {"best_model": report.get("best_model"), "comparison": report.get("comparison", [])}
    return {"best_model": None, "comparison": [], "message": "Modèles non entraînés (lancez make train)."}


@router.get("/images/{year}", tags=["data"])
def image_meta(year: int):
    """Métadonnées du composite satellite d'une année."""
    if year not in ANALYSIS_YEARS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Année non disponible")
    return {
        "year": year, "source": "Sentinel-2 SR Harmonized (composite saison sèche)",
        "bands": ["B2", "B3", "B4", "B8", "B11", "B12"],
        "center": {"lat": settings.study_area_lat, "lon": settings.study_area_lon},
    }


# ── Routes admin ──
@router.get("/admin/users", response_model=list[UserOut], tags=["admin"])
def admin_users(_: User = Depends(auth.require_role("admin")), db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/admin/logs", tags=["admin"])
def admin_logs(_: User = Depends(auth.require_role("admin")), db: Session = Depends(get_db)):
    from src.api.database import ApiLog

    logs = db.query(ApiLog).order_by(ApiLog.timestamp.desc()).limit(100).all()
    return [
        {"endpoint": l.endpoint, "method": l.method, "status_code": l.status_code,
         "timestamp": l.timestamp.isoformat() if l.timestamp else None}
        for l in logs
    ]
