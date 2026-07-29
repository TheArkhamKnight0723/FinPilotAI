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
    """Handles application startup and shutdown lifecycle."""
    logger.info(
        "Starting %s v%s [env=%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


# ── Application Factory ────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    """Creates and fully configures the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="FinPilot AI – Intelligent Financial Navigation Platform",
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
