"""
FinPilot AI – API v1 Root Router
Aggregates all v1 sub-routers. New feature routers are registered here.
"""

from fastapi import APIRouter

from app.auth.router import router as auth_router

api_v1_router = APIRouter(prefix="/api/v1")

# ── Auth ──────────────────────────────────────────────────────────────────────
api_v1_router.include_router(auth_router)

# ── Future Feature Routers (uncomment as implemented) ─────────────────────────
# from app.portfolio.router import router as portfolio_router
# api_v1_router.include_router(portfolio_router, prefix="/portfolios", tags=["Portfolio"])

# from app.market.router import router as market_router
# api_v1_router.include_router(market_router, prefix="/market", tags=["Market"])

# from app.news.router import router as news_router
# api_v1_router.include_router(news_router, prefix="/news", tags=["News"])

# from app.ai.router import router as ai_router
# api_v1_router.include_router(ai_router, prefix="/ai", tags=["AI"])
