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

image_path = Path("storage/images")
image_path.mkdir(parents=True, exist_ok=True)
app.mount("/images", StaticFiles(directory=str(image_path)), name="images")

# Attestations de licence de centre (PDF)
certificates_path = Path("storage/certificates")
certificates_path.mkdir(parents=True, exist_ok=True)
app.mount("/certificates", StaticFiles(directory=str(certificates_path)), name="certificates")

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
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    detail = str(exc) if settings.DEBUG else "Une erreur interne est survenue."
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message=detail).model_dump(),
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