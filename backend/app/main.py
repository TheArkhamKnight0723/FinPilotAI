"""
FinPilot AI – FastAPI Application Entry Point
Creates and configures the FastAPI application instance.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers
from app.middleware.cors import register_cors
from app.middleware.logging import RequestLoggingMiddleware

# ── Bootstrap logging before anything else ────────────────────────────────────
setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan (startup / shutdown events) ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handles application startup and shutdown lifecycle.
    On startup: creates all database tables (dev convenience).
    On shutdown: disposes the engine connection pool.
    """
    logger.info(
        "Starting %s v%s [env=%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )

    # ── Database table creation (dev / SQLite mode) ───────────────────────────
    # In production, Alembic migrations manage the schema.
    # This block auto-creates tables for local development convenience.
    from app.database.base import Base
    from app.database.session import engine
    import app.models.user  # noqa: F401 — ensure model is registered

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified / created.")

    yield

    # ── Cleanup ───────────────────────────────────────────────────────────────
    await engine.dispose()
    logger.info("Shutting down %s — DB connections closed.", settings.APP_NAME)


# ── Application Factory ────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    """Creates and fully configures the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "**FinPilot AI** – Intelligent Financial Navigation Platform\n\n"
            "All endpoints are versioned under `/api/v1/`. "
            "Protected endpoints require `Authorization: Bearer <token>`."
        ),
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters: outermost first) ────────────────────────────
    register_cors(app)
    app.add_middleware(RequestLoggingMiddleware)

    # ── Exception Handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_v1_router)

    # ── Root & Health Endpoints ───────────────────────────────────────────────
    @app.get("/", tags=["Root"], summary="API Root")
    async def root() -> JSONResponse:
        return JSONResponse(
            content={
                "success": True,
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.APP_ENV,
                "docs": "/docs",
            }
        )

    @app.get("/health", tags=["Health"], summary="Health Check")
    async def health() -> JSONResponse:
        return JSONResponse(
            content={
                "success": True,
                "status": "healthy",
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
            }
        )

    logger.info("Application configured successfully.")
    return app


# ── Application Instance ───────────────────────────────────────────────────────
app = create_app()
