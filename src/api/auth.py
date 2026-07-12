"""
Authentification : hachage bcrypt, JWT (access + refresh), OTP 2FA (PyOTP),
dépendances FastAPI de protection des routes et contrôle de rôle.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
import pyotp
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.settings import settings
from src.api.database import User, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


# ── Mots de passe (bcrypt) ──
def hash_password(password: str) -> str:
    # bcrypt limite l'entrée à 72 octets
    pw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ── OTP / 2FA ──
def generate_otp_secret() -> str:
    return pyotp.random_base32()


def otp_provisioning_uri(secret: str, email: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="DeforestWatch-DRC")


def verify_otp(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def check_login_otp(user: "User", code: Optional[str]) -> bool:
    """2FA imposée à la connexion.

    - Si `require_2fa` est désactivé (déploiement sans 2FA), on laisse passer.
    - En mode démo, le code statique documenté (`demo_otp_code`) est accepté,
      ce qui garde la démo « clé en main » sans compte Google Authenticator.
    - Sinon, on vérifie le vrai code TOTP du secret de l'utilisateur.
    """
    if not settings.require_2fa:
        return True
    if not code:
        return False
    if settings.demo_mode and code == settings.demo_otp_code:
        return True
    return verify_otp(user.otp_secret, code)


# ── JWT ──
def _create_token(data: dict, expires: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(email: str, role: str) -> str:
    return _create_token({"sub": email, "role": role, "type": "access"},
                         timedelta(minutes=settings.jwt_expiration_minutes))


def create_refresh_token(email: str) -> str:
    return _create_token({"sub": email, "type": "refresh"}, timedelta(days=7))


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Token invalide : {exc}")


# ── Dépendances FastAPI ──
def get_current_user(token: Optional[str] = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentification requise")
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Type de token invalide")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable ou inactif")
    return user


def require_role(role: str):
    """Fabrique une dépendance qui exige un rôle précis (ex. 'admin')."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Rôle '{role}' requis")
        return user

    return checker
