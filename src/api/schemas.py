"""Schémas Pydantic (validation des requêtes/réponses)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    otp_code: Optional[str] = Field(default=None, min_length=6, max_length=6)


class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    email: str
    otp_provisioning_uri: str
    message: str = "Compte créé. Scannez l'URI OTP dans Google Authenticator."


class StatisticItem(BaseModel):
    year: int
    total_forest_ha: float
    forest_loss_ha: float
    deforestation_rate: float


class ModelInfo(BaseModel):
    model_name: str
    accuracy: float
    f1_score: float
    mean_iou: float


class PredictionZone(BaseModel):
    lat: float
    lon: float
    risk_score: float


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LogOut(BaseModel):
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertOut(BaseModel):
    id: str
    sector: str
    lat: float
    lon: float
    year: int
    area_lost_ha: float
    severity: str
    forest_before_ha: float
    forest_after_ha: float


class ReportIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    description: str = Field(min_length=3, max_length=1000)
    reporter: Optional[str] = None


class ReportOut(BaseModel):
    id: int
    lat: float
    lon: float
    description: str
    reporter: Optional[str] = None
    severity: str
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
