"""Insights routes - What changed and why it matters."""

from typing import Optional
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


# Models
class InsightSeverity(str, Enum):
    """Insight severity level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InsightType(str, Enum):
    """Type of insight."""
    TREND_CHANGE = "trend_change"
    VOLATILITY_CHANGE = "volatility_change"
    EARNINGS_ALERT = "earnings_alert"
    FUNDAMENTAL_CHANGE = "fundamental_change"
    RISK_CHANGE = "risk_change"
    PRICE_ALERT = "price_alert"


class StockInsight(BaseModel):
    """Single insight for a stock."""
    id: str
    symbol: str
    insight_type: InsightType
    severity: InsightSeverity
    
    # What changed
    title: str
    description: str
    
    # Why it matters
    significance: str
    
    # What would invalidate this
    invalidation: Optional[str] = None
    
    # Context
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    created_at: datetime
    acknowledged: bool = False


class PortfolioInsightSummary(BaseModel):
    """Summary of insights for a portfolio."""
    portfolio_id: str
    portfolio_name: str
    total_insights: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    stocks_with_changes: list[str]
    last_generated: datetime


class WeeklyReport(BaseModel):
    """Weekly 'what changed' report."""
    portfolio_id: str
    week_start: datetime
    week_end: datetime
    
    # Summary
    summary: str
    total_changes: int
    
    # Per-stock insights
    insights: list[StockInsight]
    
    # Top concerns
    top_concerns: list[str]
    
    # What to watch
    watch_items: list[str]


# Routes
@router.get("/portfolio/{portfolio_id}", response_model=list[StockInsight])
async def get_portfolio_insights(
    portfolio_id: str,
    severity: Optional[InsightSeverity] = None,
    limit: int = Query(default=20, le=100)
):
    """
    Get all insights for a portfolio.
    
    - **severity**: Filter by severity level
    - **limit**: Maximum number of insights to return
    """
    # TODO: Implement with database/snapshot comparison
    return [
        StockInsight(
            id="insight-1",
            symbol="AAPL",
            insight_type=InsightType.TREND_CHANGE,
            severity=InsightSeverity.MEDIUM,
            title="Trend shifted from sideways to up",
            description="AAPL has broken above its 50-day moving average with increasing volume",
            significance="This often signals the start of a new upward trend",
            invalidation="A close below $175 would invalidate this signal",
            old_value="sideways",
            new_value="up",
            created_at=datetime.utcnow(),
            acknowledged=False
        )
    ]


@router.get("/portfolio/{portfolio_id}/summary", response_model=PortfolioInsightSummary)
async def get_portfolio_insight_summary(portfolio_id: str):
    """
    Get summary of insights for a portfolio.
    
    Quick overview of what needs attention.
    """
    # TODO: Implement
    return PortfolioInsightSummary(
        portfolio_id=portfolio_id,
        portfolio_name="My Portfolio",
        total_insights=5,
        critical_count=0,
        high_count=1,
        medium_count=2,
        low_count=2,
        stocks_with_changes=["AAPL", "MSFT"],
        last_generated=datetime.utcnow()
    )


@router.get("/stock/{symbol}", response_model=list[StockInsight])
async def get_stock_insights(symbol: str, limit: int = Query(default=10, le=50)):
    """
    Get recent insights for a specific stock.
    """
    # TODO: Implement
    return [
        StockInsight(
            id="insight-2",
            symbol=symbol.upper(),
            insight_type=InsightType.EARNINGS_ALERT,
            severity=InsightSeverity.MEDIUM,
            title="Earnings report in 10 days",
            description=f"{symbol.upper()} will report earnings on January 25th",
            significance="Stock may see increased volatility around earnings",
            invalidation=None,
            created_at=datetime.utcnow(),
            acknowledged=False
        )
    ]


@router.get("/portfolio/{portfolio_id}/weekly", response_model=WeeklyReport)
async def get_weekly_report(portfolio_id: str):
    """
    Get weekly 'what changed' report.
    
    This is the main MVP deliverable - a clear summary
    of what changed in the portfolio this week.
    """
    # TODO: Implement with LLM for summarization
    return WeeklyReport(
        portfolio_id=portfolio_id,
        week_start=datetime.utcnow(),
        week_end=datetime.utcnow(),
        summary="Your portfolio had 3 notable changes this week. AAPL showed trend improvement while TSLA volatility increased significantly.",
        total_changes=3,
        insights=[],
        top_concerns=["TSLA volatility spike - monitor closely"],
        watch_items=["MSFT earnings next week", "NVDA near 52-week high"]
    )


@router.post("/acknowledge/{insight_id}")
async def acknowledge_insight(insight_id: str):
    """
    Mark an insight as acknowledged/read.
    """
    # TODO: Implement
    return {"message": f"Insight {insight_id} acknowledged"}


@router.get("/unacknowledged")
async def get_unacknowledged_insights(limit: int = Query(default=20, le=100)):
    """
    Get all unacknowledged insights across portfolios.
    """
    # TODO: Implement
    return []
