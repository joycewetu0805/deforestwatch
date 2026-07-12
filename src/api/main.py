"""
Application FastAPI DeforestWatch-DRC.
CORS, documentation Swagger auto, logging des requêtes, gestion d'erreurs,
initialisation de la base et seed admin au démarrage.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from config.settings import production_config_problems, settings
from src.api.database import ApiLog, SessionLocal, User, init_db
from src.api import auth
from src.api.routes import router
from src.utils.logger import get_logger

log = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail-fast : refuse de démarrer en production avec une config dangereuse.
    problems = production_config_problems(settings)
    if problems:
        raise RuntimeError(
            "Configuration de production non sécurisée : "
            + " ; ".join(problems)
            + ". Corrigez le .env avant de déployer."
        )
    init_db()
    _seed_admin()
    yield


app = FastAPI(
    title="DeforestWatch-DRC API",
    description="API de surveillance et prédiction de la déforestation au Mai-Ndombe (RDC).",
    version="1.0.0",
    lifespan=lifespan,
)

_cors_origins = settings.cors_origins_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # credentials + "*" est une combinaison invalide/refusée par les navigateurs ;
    # l'API s'authentifie par Bearer token, pas par cookie.
    allow_credentials="*" not in _cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ensure_user(db, email: str, password: str, role: str) -> None:
    if not db.query(User).filter(User.email == email).first():
        db.add(User(
            email=email,
            password_hash=auth.hash_password(password),
            otp_secret=auth.generate_otp_secret(),
            role=role,
        ))
        db.commit()
        log.info(f"Compte {role} créé : {email}")


def _seed_admin():
    """Crée les comptes admin selon le mode.

    - Mode démo : compte documenté admin@deforestwatch.cd / admin123.
    - Production : compte optionnel bootstrappé depuis ADMIN_EMAIL / ADMIN_PASSWORD.
    """
    db = SessionLocal()
    try:
        if settings.demo_mode:
            _ensure_user(db, "admin@deforestwatch.cd", "admin123", "admin")
        if settings.admin_email and settings.admin_password:
            _ensure_user(db, settings.admin_email, settings.admin_password, "admin")
    finally:
        db.close()


def _persist_request_log(path: str, method: str, status_code: int) -> None:
    """Écriture DB synchrone du log de requête (best-effort)."""
    db = SessionLocal()
    try:
        db.add(ApiLog(endpoint=path, method=method, status_code=status_code))
        db.commit()
    finally:
        db.close()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    # journalise en base hors de l'event loop (best-effort, ne bloque pas)
    try:
        await run_in_threadpool(
            _persist_request_log, request.url.path, request.method, response.status_code
        )
    except Exception:
        pass
    log.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.0f}ms)")
    return response


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    log.error(f"Erreur non gérée : {exc}")
    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur"})


@app.get("/", tags=["meta"])
def root():
    return {
        "app": "DeforestWatch-DRC",
        "version": "1.0.0",
        "docs": "/docs",
        "demo_mode": settings.demo_mode,
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


app.include_router(router)
