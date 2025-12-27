"""Stock information and analysis routes."""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

router = APIRouter()


# Response Models
class StockPrice(BaseModel):
    """Current stock price info."""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime


class StockInfo(BaseModel):
    """Basic stock information."""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    dividend_yield: Optional[float] = None


class StockStatus(BaseModel):
    """Stock status for portfolio view."""
    symbol: str
    status: str  # healthy, watch, risky
    trend: str   # up, down, sideways
    volatility: str  # low, normal, high
    risk_score: float
    last_updated: datetime


class StockAnalysis(BaseModel):
    """Full stock analysis."""
    symbol: str
    
    # Status
    status: str
    status_reason: str
    
    # Trend analysis
    trend_direction: str
    trend_strength: float
    above_ma_20: bool
    above_ma_50: bool
    
    # Risk analysis
    risk_level: str
    risk_score: float
    volatility_percentile: float
    
    # Fundamentals
    fundamental_health: str
    valuation: str
    
    # Context
    days_to_earnings: Optional[int] = None
    price_vs_52w_high: float
    price_vs_52w_low: float
    
    analyzed_at: datetime


# Routes
@router.get("/search")
async def search_stocks(q: str = Query(..., min_length=1, max_length=10)):
    """
    Search for stocks by symbol or name.
    
    - **q**: Search query (ticker symbol or company name)
    """
    # TODO: Implement with Yahoo Finance or other provider
    return [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
    ]


@router.get("/{symbol}/price", response_model=StockPrice)
async def get_stock_price(symbol: str):
    """
    Get current price for a stock.
    """
    # TODO: Implement with data provider
    return StockPrice(
        symbol=symbol.upper(),
        price=185.50,
        change=2.35,
        change_percent=1.28,
        volume=45000000,
        timestamp=datetime.utcnow()
    )


@router.get("/{symbol}/info", response_model=StockInfo)
async def get_stock_info(symbol: str):
    """
    Get basic information for a stock.
    """
    # TODO: Implement with data provider
    return StockInfo(
        symbol=symbol.upper(),
        name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        market_cap=2850000000000,
        pe_ratio=28.5,
        forward_pe=25.2,
        dividend_yield=0.52
    )


@router.get("/{symbol}/status", response_model=StockStatus)
async def get_stock_status(symbol: str):
    """
    Get current status for portfolio display.
    
    Returns simplified status: healthy, watch, or risky.
    """
    # TODO: Implement with snapshot/analysis
    return StockStatus(
        symbol=symbol.upper(),
        status="healthy",
        trend="up",
        volatility="normal",
        risk_score=35.5,
        last_updated=datetime.utcnow()
    )


@router.get("/{symbol}/analysis", response_model=StockAnalysis)
async def get_stock_analysis(symbol: str):
    """
    Get full analysis for a stock.
    
    Includes trend, risk, and fundamental analysis.
    This is the detailed view for a single stock.
    """
    # TODO: Implement with full analysis pipeline
    return StockAnalysis(
        symbol=symbol.upper(),
        status="healthy",
        status_reason="Strong uptrend with normal volatility",
        trend_direction="up",
        trend_strength=0.75,
        above_ma_20=True,
        above_ma_50=True,
        risk_level="moderate",
        risk_score=42.0,
        volatility_percentile=55.0,
        fundamental_health="healthy",
        valuation="fair",
        days_to_earnings=23,
        price_vs_52w_high=5.2,
        price_vs_52w_low=32.1,
        analyzed_at=datetime.utcnow()
    )


@router.post("/{symbol}/refresh")
async def refresh_stock_data(symbol: str):
    """
    Force refresh of stock data and analysis.
    
    Triggers new snapshot creation and comparison.
    """
    # TODO: Implement refresh logic
    return {
        "message": f"Refresh triggered for {symbol.upper()}",
        "status": "processing"
    }
