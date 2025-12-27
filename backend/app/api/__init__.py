"""API routes module."""

from fastapi import APIRouter

from .auth import router as auth_router
from .portfolio import router as portfolio_router
from .stocks import router as stocks_router
from .insights import router as insights_router
from .snapshots import router as snapshots_router

router = APIRouter()

# Include all route modules
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
router.include_router(stocks_router, prefix="/stocks", tags=["Stocks"])
router.include_router(insights_router, prefix="/insights", tags=["Insights"])
router.include_router(snapshots_router, prefix="/snapshots", tags=["Snapshots"])
