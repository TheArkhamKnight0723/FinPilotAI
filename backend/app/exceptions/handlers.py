"""
FinPilot AI – Global Exception Handlers
Registers FastAPI exception handlers that return consistent JSON error responses.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import FinPilotBaseException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI app instance."""

    @app.exception_handler(FinPilotBaseException)
    async def finpilot_exception_handler(
        request: Request, exc: FinPilotBaseException
    ) -> JSONResponse:
        logger.error(
            "Application error",
            extra={"path": request.url.path, "message": exc.message},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception",
            extra={"path": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"},
        )
