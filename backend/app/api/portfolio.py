"""Portfolio management routes."""

from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

router = APIRouter()


# Request/Response Models
class StockHolding(BaseModel):
    """Stock holding in portfolio."""
    symbol: str
    shares: float
    avg_cost: Optional[float] = None
    added_at: datetime


class PortfolioCreate(BaseModel):
    """Create portfolio request."""
    name: str
    description: Optional[str] = None


class PortfolioResponse(BaseModel):
    """Portfolio response model."""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    holdings: list[StockHolding]
    created_at: datetime
    updated_at: datetime


class PortfolioSummary(BaseModel):
    """Portfolio summary with status."""
    id: str
    name: str
    total_holdings: int
    healthy_count: int
    watch_count: int
    risky_count: int
    has_changes: bool
    last_checked: Optional[datetime] = None


class AddStockRequest(BaseModel):
    """Add stock to portfolio request."""
    symbol: str
    shares: float
    avg_cost: Optional[float] = None


# Routes
@router.get("/", response_model=list[PortfolioSummary])
async def list_portfolios():
    """
    List all portfolios for current user.
    
    Returns summary view with status counts.
    """
    # TODO: Implement with database
    return [
        PortfolioSummary(
            id="demo-portfolio",
            name="My Portfolio",
            total_holdings=5,
            healthy_count=3,
            watch_count=1,
            risky_count=1,
            has_changes=True,
            last_checked=datetime.utcnow()
        )
    ]


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: PortfolioCreate):
    """
    Create a new portfolio.
    
    - **name**: Portfolio name
    - **description**: Optional description
    """
    # TODO: Implement with database
    return PortfolioResponse(
        id="new-portfolio-uuid",
        user_id="user-uuid",
        name=portfolio.name,
        description=portfolio.description,
        holdings=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: str):
    """
    Get portfolio by ID with all holdings.
    """
    # TODO: Implement with database
    return PortfolioResponse(
        id=portfolio_id,
        user_id="user-uuid",
        name="My Portfolio",
        description="Demo portfolio",
        holdings=[
            StockHolding(
                symbol="AAPL",
                shares=10,
                avg_cost=150.0,
                added_at=datetime.utcnow()
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: str):
    """
    Delete a portfolio.
    """
    # TODO: Implement with database
    return None


@router.post("/{portfolio_id}/stocks", response_model=PortfolioResponse)
async def add_stock(portfolio_id: str, stock: AddStockRequest):
    """
    Add a stock to portfolio.
    
    - **symbol**: Stock ticker symbol
    - **shares**: Number of shares
    - **avg_cost**: Optional average cost basis
    """
    # TODO: Implement with database
    return PortfolioResponse(
        id=portfolio_id,
        user_id="user-uuid",
        name="My Portfolio",
        description=None,
        holdings=[
            StockHolding(
                symbol=stock.symbol,
                shares=stock.shares,
                avg_cost=stock.avg_cost,
                added_at=datetime.utcnow()
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.delete("/{portfolio_id}/stocks/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_stock(portfolio_id: str, symbol: str):
    """
    Remove a stock from portfolio.
    """
    # TODO: Implement with database
    return None


@router.get("/{portfolio_id}/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(portfolio_id: str):
    """
    Get portfolio summary with change detection status.
    
    This is the main endpoint for "what changed" view.
    """
    # TODO: Implement with snapshots
    return PortfolioSummary(
        id=portfolio_id,
        name="My Portfolio",
        total_holdings=5,
        healthy_count=3,
        watch_count=1,
        risky_count=1,
        has_changes=True,
        last_checked=datetime.utcnow()
    )
