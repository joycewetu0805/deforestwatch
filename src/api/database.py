"""
Couche base de données SQLAlchemy (PostgreSQL / Supabase).
En l'absence de PostgreSQL, repli automatique sur SQLite local pour que l'API
démarre partout (démo, CI, soutenance).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings
from src.utils.logger import get_logger

log = get_logger("database")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")           # admin / user
    otp_secret = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True)
    year = Column(Integer, index=True)
    total_forest_ha = Column(Float)
    forest_loss_ha = Column(Float)
    deforestation_rate = Column(Float)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    zone_lat = Column(Float)
    zone_lon = Column(Float)
    risk_score = Column(Float)
    predicted_year = Column(Integer)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiLog(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    version = Column(String)
    accuracy = Column(Float)
    f1_score = Column(Float)
    mean_iou = Column(Float)
    file_path = Column(String)
    deployed_at = Column(DateTime, default=datetime.utcnow)


def _make_engine():
    url = settings.database_url
    try:
        engine = create_engine(url, pool_pre_ping=True)
        engine.connect().close()
        log.info("Connecté à PostgreSQL.")
        return engine
    except Exception as exc:
        log.warning(f"PostgreSQL indisponible ({exc}). Repli SQLite local.")
        from config.settings import DATA_DIR

        return create_engine(f"sqlite:///{DATA_DIR / 'deforestwatch.db'}",
                             connect_args={"check_same_thread": False})


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    log.info("Schéma de base de données initialisé.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
