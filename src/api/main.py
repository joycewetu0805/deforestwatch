"""
Application FastAPI DeforestWatch-DRC.
CORS, documentation Swagger auto, logging des requêtes, gestion d'erreurs,
initialisation de la base et seed admin au démarrage.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings
from src.api.database import ApiLog, SessionLocal, User, init_db
from src.api import auth
from src.api.routes import router
from src.utils.logger import get_logger

log = get_logger("api")

app = FastAPI(
    title="DeforestWatch-DRC API",
    description="API de surveillance et prédiction de la déforestation au Mai-Ndombe (RDC).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    _seed_admin()


def _seed_admin():
    """Crée un compte admin par défaut en mode démo (admin@deforestwatch.cd / admin123)."""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@deforestwatch.cd").first():
            db.add(User(
                email="admin@deforestwatch.cd",
                password_hash=auth.hash_password("admin123"),
                otp_secret=auth.generate_otp_secret(),
                role="admin",
            ))
            db.commit()
            log.info("Compte admin de démo créé : admin@deforestwatch.cd / admin123")
    finally:
        db.close()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    # journalise la requête en base (best-effort)
    try:
        db = SessionLocal()
        db.add(ApiLog(endpoint=request.url.path, method=request.method,
                      status_code=response.status_code))
        db.commit()
        db.close()
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
