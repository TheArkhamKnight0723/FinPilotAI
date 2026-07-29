"""
FinPilot AI – CORS Middleware Configuration
Configures allowed origins, methods, and headers for cross-origin requests.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings


def register_cors(app: FastAPI) -> None:
    """Attach CORS middleware to the FastAPI application."""
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
