"""
app/main.py — DeutschTest API
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import get_settings
from app.shared.database.session import engine
from app.shared.schemas.responses import ErrorResponse

settings = get_settings()
logger = logging.getLogger("deutschtest")


# ── Logging setup ────────────────────────────
def setup_logging() -> None:
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


# ── Lifespan ─────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("=" * 55)
    logger.info("🚀 DeutschTest API starting")
    logger.info(f"   env={settings.APP_ENV}  debug={settings.DEBUG}")

    # Vérifier connexion DB
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("✅ Database connection OK")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

    # Créer dossiers storage si absents
    for folder in ["storage/audio", "storage/images", "storage/temp", "storage/certificates"]:
        Path(folder).mkdir(parents=True, exist_ok=True)

    logger.info("🎉 Startup complete")
    logger.info("=" * 55)

    yield

    # Shutdown
    await engine.dispose()
    logger.info("👋 DeutschTest API shutdown")


# ── App ──────────────────────────────────────
app = FastAPI(
    title="DeutschTest API",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Static files (audio) ────────────────────
audio_path = Path("storage/audio")
audio_path.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(audio_path)), name="audio")

dts_path = Path("storage/start-deutsch")
dts_path.mkdir(parents=True, exist_ok=True)
app.mount("/start-deutsch", StaticFiles(directory=str(dts_path)), name="start-deutsch")

image_path = Path("storage/images")
image_path.mkdir(parents=True, exist_ok=True)
app.mount("/images", StaticFiles(directory=str(image_path)), name="images")

# Attestations de licence de centre (PDF)
certificates_path = Path("storage/certificates")
certificates_path.mkdir(parents=True, exist_ok=True)
app.mount("/certificates", StaticFiles(directory=str(certificates_path)), name="certificates")


# Reçus/factures PDF (paiements examens + paiements enrollments)
invoices_path = Path("storage/invoices")
invoices_path.mkdir(parents=True, exist_ok=True)
app.mount("/invoices", StaticFiles(directory=str(invoices_path)), name="invoices")

logos_path = Path("storage/center_logos")
logos_path.mkdir(parents=True, exist_ok=True)
app.mount("/center-logos", StaticFiles(directory=str(logos_path)), name="center-logos")

# ── CORS ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
     allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

# ── Exception handlers ───────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors[field] = error["msg"]
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Erreur de validation",
            detail=errors,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_detail = "Erreur interne"
    try:
        logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
        error_detail = str(exc)
    except Exception:
        logger.error(
            f"Unhandled exception on {request.url.path} "
            f"(type={type(exc).__name__}) — impossible d'afficher le détail complet.",
            exc_info=True,
        )
        # Pour une ResponseValidationError/RequestValidationError, exc.errors()
        # retourne une liste de dicts (loc/msg/type) — sûre à logger même quand
        # str(exc) plante à cause d'un objet ORM détaché dans les détails.
        errors_method = getattr(exc, "errors", None)
        if callable(errors_method):
            try:
                raw_errors = errors_method()
                safe_errors = []
                for e in raw_errors:
                    safe_errors.append({
                        "loc": e.get("loc"),
                        "msg": str(e.get("msg"))[:300],
                        "type": e.get("type"),
                    })
                logger.error(f"Détail de validation : {safe_errors}")
                error_detail = f"Erreur de validation de la réponse : {safe_errors}"
            except Exception as inner:
                logger.error(f"Impossible d'extraire exc.errors() non plus : {inner}")

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Erreur interne du serveur",
            detail=error_detail if settings.DEBUG else None,
        ).model_dump(),
    )


# ── Routers ──────────────────────────────────
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.exams.router import router as exams_router
from app.modules.exam_access.router import router as access_router
from app.modules.exam_sessions.router import router as sessions_router
from app.modules.questions.router import router as questions_router
from app.modules.partners.router import router as partners_router
from app.modules.promo_codes.router import router as promo_codes_router
from app.modules.payments.router import router as payments_router
from app.modules.plans.router import router as plans_router
from app.modules.invoices.router import router as invoices_router
from app.modules.corrections.router import router as corrections_router
from app.modules.schreiben_simulator.router import router as simulator_router
from app.modules.ai_credit_purchases.router import router as ai_credits_router
from app.modules.settings.router import router as settings_router
from app.modules.centers.router import router as centers_router
from app.modules.sprechen_agent.router import router as sprechen_router
from app.modules.referrals.router import router as referrals_router
from app.modules.enrollments.router import router as enrollments_router
from app.modules.live_session.router import router as live_session_router
from app.modules.start_deutsch.router import router as start_deutsch_router
from app.modules.training_sessions.router import router as training_sessions_router




app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(access_router, prefix="/api/v1/access", tags=["exam-access"])
app.include_router(sessions_router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(exams_router, prefix="/api/v1/exams", tags=["exams"])
app.include_router(questions_router, prefix="/api/v1", tags=["questions"])
app.include_router(partners_router, prefix="/api/v1/partners", tags=["partners"])
app.include_router(promo_codes_router, prefix="/api/v1/promo-codes", tags=["promo-codes"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(plans_router, prefix="/api/v1/plans", tags=["plans"])
app.include_router(invoices_router, prefix="/api/v1/invoices", tags=["invoices"])
app.include_router(corrections_router, prefix="/api/v1/corrections", tags=["corrections"])
app.include_router( simulator_router,  prefix="/api/v1/schreiben-simulator",  tags=["Schreiben Simulator"])
app.include_router(ai_credits_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(centers_router, prefix="/api/v1/centers", tags=["centers"])
app.include_router(sprechen_router, prefix="/api/v1/sprechen-simulator", tags=["sprechen-simulator"])
app.include_router(referrals_router, prefix="/api/v1/referrals", tags=["referrals"])
app.include_router(enrollments_router, prefix="/api/v1/enrollments", tags=["enrollments"])
app.include_router(live_session_router, prefix="/api/v1/live-session", tags=["live-session"])
app.include_router(start_deutsch_router, prefix="/api/v1/start-deutsch", tags=["start-deutsch"])
app.include_router(training_sessions_router, prefix="/api/v1/training-sessions", tags=["training-sessions"])










# ── Health ───────────────────────────────────
@app.get("/health", tags=["system"])
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "env": settings.APP_ENV,
        "database": db_status,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8005, reload=True)