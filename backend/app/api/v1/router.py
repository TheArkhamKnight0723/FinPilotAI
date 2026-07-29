"""
FinPilot AI – API v1 Root Router
Aggregates all v1 sub-routers. New feature routers are registered here.
"""

from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")

# Feature routers will be imported and included here as they are implemented.
# Example:
#   from app.api.v1.portfolio import router as portfolio_router
#   api_v1_router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
