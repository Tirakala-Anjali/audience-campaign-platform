import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError as SAOperationalError

from app.core.config import settings
from app.routers import health
from app.routers import auth as auth_router
from app.routers import campaigns as campaigns_router
from app.routers import dashboard as dashboard_router
from app.routers import audience as audience_router
from app.routers import segments as segments_router
from app.routers import templates as templates_router

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — allow the React dev server origin
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup event — seed default roles idempotently
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    """Run once at startup: seed default roles into the database."""
    try:
        from app.database import SessionLocal
        from app.routers.auth import seed_roles
        db = SessionLocal()
        seed_roles(db)
        db.close()
        logger.info("Role seeding complete.")
    except Exception as exc:
        # If DB is not yet available (e.g., before first migration) just log
        logger.warning("Role seeding skipped (DB may not be ready): %s", exc)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router)
app.include_router(auth_router.router)
app.include_router(campaigns_router.router)
app.include_router(dashboard_router.router)
app.include_router(audience_router.router)
app.include_router(segments_router.router)
app.include_router(templates_router.router)

# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------


@app.get("/", tags=["Root"], summary="API root")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# ---------------------------------------------------------------------------
# Global exception handler — never expose internal details
# ---------------------------------------------------------------------------


@app.exception_handler(SAOperationalError)
async def db_operational_error_handler(request: Request, exc: SAOperationalError):
    """Catch unhandled DB connection errors and return 503 instead of 500."""
    logger.error("DB OperationalError on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database is currently unavailable. Please try again shortly."},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )
