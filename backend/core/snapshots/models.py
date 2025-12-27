"""Snapshot data models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TrendState(str, Enum):
    """Stock trend classification."""
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"


class VolatilityBucket(str, Enum):
    """Volatility classification."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class FundamentalHealth(str, Enum):
    """Fundamental health status."""
    HEALTHY = "healthy"
    WATCH = "watch"
    RISKY = "risky"


class StockSnapshot(BaseModel):
    """
    Point-in-time state snapshot for a stock.
    
    This is the core data structure for change detection.
    Compare Snapshot_T1 - Snapshot_T0 to detect material changes.
    """
    symbol: str
    timestamp: datetime
    
    # Trend state
    trend_state: TrendState
    trend_strength: float  # 0-1, how strong the trend is
    
    # Volatility
    volatility_bucket: VolatilityBucket
    volatility_percentile: float  # 0-100
    
    # Price context
    current_price: float
    price_vs_52w_high: float  # percentage below 52w high
    price_vs_52w_low: float   # percentage above 52w low
    
    # Events
    days_to_earnings: Optional[int] = None
    in_earnings_window: bool = False
    
    # Fundamentals (basic)
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    fundamental_health: FundamentalHealth = FundamentalHealth.HEALTHY
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "timestamp": "2025-01-15T00:00:00Z",
                "trend_state": "up",
                "trend_strength": 0.75,
                "volatility_bucket": "normal",
                "volatility_percentile": 45.0,
                "current_price": 185.50,
                "price_vs_52w_high": 5.2,
                "price_vs_52w_low": 32.1,
                "days_to_earnings": 15,
                "in_earnings_window": False,
                "pe_ratio": 28.5,
                "market_cap": 2850000000000,
                "fundamental_health": "healthy"
            }
        }


class ChangeType(str, Enum):
    """Type of change detected."""
    TREND_REVERSAL = "trend_reversal"
    VOLATILITY_SPIKE = "volatility_spike"
    VOLATILITY_DROP = "volatility_drop"
    EARNINGS_APPROACHING = "earnings_approaching"
    FUNDAMENTAL_SHIFT = "fundamental_shift"
    PRICE_BREAKOUT = "price_breakout"
    PRICE_BREAKDOWN = "price_breakdown"
    NO_MATERIAL_CHANGE = "no_material_change"


class ChangeSeverity(str, Enum):
    """Severity of detected change."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SnapshotChange(BaseModel):
    """Individual change detected between snapshots."""
    change_type: ChangeType
    severity: ChangeSeverity
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class SnapshotDiff(BaseModel):
    """
    Difference between two snapshots.
    This is the output of change detection.
    """
    symbol: str
    from_timestamp: datetime
    to_timestamp: datetime
    
    # List of detected changes
    changes: list[SnapshotChange]
    
    # Summary
    has_material_change: bool
    overall_severity: ChangeSeverity
    summary: str  # Human-readable summary
    
    # Status change
    status_changed: bool
    old_status: FundamentalHealth
    new_status: FundamentalHealth
