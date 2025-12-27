"""Tests for snapshot functionality."""

import pytest
from datetime import datetime
import pandas as pd
import numpy as np

from core.snapshots.builder import SnapshotBuilder
from core.snapshots.comparator import SnapshotComparator
from core.snapshots.models import (
    StockSnapshot,
    TrendState,
    VolatilityBucket,
    FundamentalHealth,
    ChangeType,
    ChangeSeverity,
)


def create_mock_price_data(days: int = 60, trend: str = "up") -> pd.DataFrame:
    """Create mock price data for testing."""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    if trend == "up":
        base_prices = np.linspace(100, 120, days) + np.random.randn(days) * 2
    elif trend == "down":
        base_prices = np.linspace(120, 100, days) + np.random.randn(days) * 2
    else:  # sideways
        base_prices = 110 + np.random.randn(days) * 3
    
    return pd.DataFrame({
        'Open': base_prices - 0.5,
        'High': base_prices + 1.5,
        'Low': base_prices - 1.5,
        'Close': base_prices,
        'Volume': np.random.randint(1000000, 5000000, days)
    }, index=dates)


class TestSnapshotBuilder:
    """Tests for SnapshotBuilder."""
    
    def test_build_snapshot_uptrend(self):
        """Test building snapshot for uptrending stock."""
        builder = SnapshotBuilder()
        price_data = create_mock_price_data(trend="up")
        
        snapshot = builder.build_snapshot(
            symbol="TEST",
            price_data=price_data,
            fundamentals={'pe_ratio': 25.0}
        )
        
        assert snapshot.symbol == "TEST"
        assert snapshot.trend_state == TrendState.UP
        assert snapshot.current_price > 0
    
    def test_build_snapshot_downtrend(self):
        """Test building snapshot for downtrending stock."""
        builder = SnapshotBuilder()
        price_data = create_mock_price_data(trend="down")
        
        snapshot = builder.build_snapshot(
            symbol="TEST",
            price_data=price_data
        )
        
        assert snapshot.trend_state == TrendState.DOWN
    
    def test_build_snapshot_with_earnings(self):
        """Test building snapshot with earnings date."""
        builder = SnapshotBuilder()
        price_data = create_mock_price_data()
        
        from datetime import timedelta
        earnings_date = datetime.now() + timedelta(days=10)
        
        snapshot = builder.build_snapshot(
            symbol="TEST",
            price_data=price_data,
            earnings_date=earnings_date
        )
        
        assert snapshot.days_to_earnings is not None
        assert snapshot.in_earnings_window == True


class TestSnapshotComparator:
    """Tests for SnapshotComparator."""
    
    def test_detect_trend_reversal(self):
        """Test detecting trend reversal."""
        comparator = SnapshotComparator()
        
        old = StockSnapshot(
            symbol="TEST",
            timestamp=datetime.now(),
            trend_state=TrendState.UP,
            trend_strength=0.7,
            volatility_bucket=VolatilityBucket.NORMAL,
            volatility_percentile=50.0,
            current_price=100.0,
            price_vs_52w_high=5.0,
            price_vs_52w_low=20.0,
            fundamental_health=FundamentalHealth.HEALTHY
        )
        
        new = StockSnapshot(
            symbol="TEST",
            timestamp=datetime.now(),
            trend_state=TrendState.DOWN,
            trend_strength=0.6,
            volatility_bucket=VolatilityBucket.NORMAL,
            volatility_percentile=55.0,
            current_price=95.0,
            price_vs_52w_high=10.0,
            price_vs_52w_low=15.0,
            fundamental_health=FundamentalHealth.HEALTHY
        )
        
        diff = comparator.compare(old, new)
        
        assert diff.has_material_change == True
        assert any(c.change_type == ChangeType.TREND_REVERSAL for c in diff.changes)
    
    def test_no_material_change(self):
        """Test when no material change detected."""
        comparator = SnapshotComparator()
        
        old = StockSnapshot(
            symbol="TEST",
            timestamp=datetime.now(),
            trend_state=TrendState.UP,
            trend_strength=0.7,
            volatility_bucket=VolatilityBucket.NORMAL,
            volatility_percentile=50.0,
            current_price=100.0,
            price_vs_52w_high=5.0,
            price_vs_52w_low=20.0,
            fundamental_health=FundamentalHealth.HEALTHY
        )
        
        new = StockSnapshot(
            symbol="TEST",
            timestamp=datetime.now(),
            trend_state=TrendState.UP,
            trend_strength=0.75,
            volatility_bucket=VolatilityBucket.NORMAL,
            volatility_percentile=52.0,
            current_price=102.0,
            price_vs_52w_high=4.0,
            price_vs_52w_low=22.0,
            fundamental_health=FundamentalHealth.HEALTHY
        )
        
        diff = comparator.compare(old, new)
        
        assert diff.has_material_change == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
