"""Snapshot management routes."""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from core.snapshots.models import (
    StockSnapshot,
    SnapshotDiff,
    TrendState,
    VolatilityBucket,
    FundamentalHealth,
    ChangeSeverity,
)

router = APIRouter()


# Response Models
class SnapshotResponse(BaseModel):
    """Snapshot response with metadata."""
    id: str
    snapshot: StockSnapshot
    created_at: datetime


class SnapshotCompareResponse(BaseModel):
    """Comparison response."""
    symbol: str
    from_snapshot: SnapshotResponse
    to_snapshot: SnapshotResponse
    diff: SnapshotDiff


class SnapshotHistoryItem(BaseModel):
    """Item in snapshot history."""
    id: str
    symbol: str
    timestamp: datetime
    trend_state: TrendState
    volatility_bucket: VolatilityBucket
    fundamental_health: FundamentalHealth
    current_price: float


# Routes
@router.get("/stock/{symbol}/latest", response_model=SnapshotResponse)
async def get_latest_snapshot(symbol: str):
    """
    Get the most recent snapshot for a stock.
    """
    # TODO: Implement with database
    return SnapshotResponse(
        id="snapshot-uuid",
        snapshot=StockSnapshot(
            symbol=symbol.upper(),
            timestamp=datetime.utcnow(),
            trend_state=TrendState.UP,
            trend_strength=0.72,
            volatility_bucket=VolatilityBucket.NORMAL,
            volatility_percentile=48.0,
            current_price=185.50,
            price_vs_52w_high=5.2,
            price_vs_52w_low=32.1,
            days_to_earnings=23,
            in_earnings_window=False,
            pe_ratio=28.5,
            market_cap=2850000000000,
            fundamental_health=FundamentalHealth.HEALTHY
        ),
        created_at=datetime.utcnow()
    )


@router.get("/stock/{symbol}/history", response_model=list[SnapshotHistoryItem])
async def get_snapshot_history(
    symbol: str,
    limit: int = Query(default=10, le=50)
):
    """
    Get snapshot history for a stock.
    
    Returns list of past snapshots to see state evolution.
    """
    # TODO: Implement with database
    return [
        SnapshotHistoryItem(
            id="snapshot-1",
            symbol=symbol.upper(),
            timestamp=datetime.utcnow(),
            trend_state=TrendState.UP,
            volatility_bucket=VolatilityBucket.NORMAL,
            fundamental_health=FundamentalHealth.HEALTHY,
            current_price=185.50
        )
    ]


@router.get("/stock/{symbol}/compare", response_model=SnapshotCompareResponse)
async def compare_snapshots(
    symbol: str,
    from_id: Optional[str] = None,
    to_id: Optional[str] = None
):
    """
    Compare two snapshots and get diff.
    
    If IDs not provided, compares latest with previous.
    This is the core change detection endpoint.
    """
    # TODO: Implement with database and comparator
    dummy_old = StockSnapshot(
        symbol=symbol.upper(),
        timestamp=datetime.utcnow(),
        trend_state=TrendState.SIDEWAYS,
        trend_strength=0.3,
        volatility_bucket=VolatilityBucket.NORMAL,
        volatility_percentile=42.0,
        current_price=175.00,
        price_vs_52w_high=10.0,
        price_vs_52w_low=25.0,
        fundamental_health=FundamentalHealth.HEALTHY
    )
    
    dummy_new = StockSnapshot(
        symbol=symbol.upper(),
        timestamp=datetime.utcnow(),
        trend_state=TrendState.UP,
        trend_strength=0.72,
        volatility_bucket=VolatilityBucket.NORMAL,
        volatility_percentile=48.0,
        current_price=185.50,
        price_vs_52w_high=5.2,
        price_vs_52w_low=32.1,
        fundamental_health=FundamentalHealth.HEALTHY
    )
    
    # Would use SnapshotComparator here
    from core.snapshots.models import SnapshotChange, ChangeType
    
    return SnapshotCompareResponse(
        symbol=symbol.upper(),
        from_snapshot=SnapshotResponse(
            id="old-snapshot",
            snapshot=dummy_old,
            created_at=datetime.utcnow()
        ),
        to_snapshot=SnapshotResponse(
            id="new-snapshot",
            snapshot=dummy_new,
            created_at=datetime.utcnow()
        ),
        diff=SnapshotDiff(
            symbol=symbol.upper(),
            from_timestamp=dummy_old.timestamp,
            to_timestamp=dummy_new.timestamp,
            changes=[
                SnapshotChange(
                    change_type=ChangeType.TREND_REVERSAL,
                    severity=ChangeSeverity.HIGH,
                    description="Trend changed from sideways to up",
                    old_value="sideways",
                    new_value="up"
                )
            ],
            has_material_change=True,
            overall_severity=ChangeSeverity.HIGH,
            summary=f"{symbol.upper()}: Trend changed from sideways to up",
            status_changed=False,
            old_status=FundamentalHealth.HEALTHY,
            new_status=FundamentalHealth.HEALTHY
        )
    )


@router.post("/stock/{symbol}/create")
async def create_snapshot(symbol: str):
    """
    Manually trigger snapshot creation for a stock.
    
    Normally done by background jobs, but can be triggered manually.
    """
    # TODO: Implement with SnapshotBuilder and data provider
    return {
        "message": f"Snapshot creation triggered for {symbol.upper()}",
        "status": "processing"
    }


@router.post("/portfolio/{portfolio_id}/create-all")
async def create_portfolio_snapshots(portfolio_id: str):
    """
    Create snapshots for all stocks in a portfolio.
    """
    # TODO: Implement
    return {
        "message": f"Snapshot creation triggered for portfolio {portfolio_id}",
        "status": "processing"
    }
