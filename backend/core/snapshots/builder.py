"""Snapshot builder - Creates state snapshots from market data."""

from datetime import datetime
from typing import Optional
import pandas as pd

from .models import (
    StockSnapshot,
    TrendState,
    VolatilityBucket,
    FundamentalHealth,
)


class SnapshotBuilder:
    """
    Builds point-in-time state snapshots for stocks.
    
    Uses recent price data (60-90 days) to determine:
    - Trend state (up/down/sideways)
    - Volatility bucket (low/normal/high)
    - Price context (vs 52w high/low)
    - Event proximity (earnings)
    """
    
    def __init__(self, lookback_days: int = 90):
        self.lookback_days = lookback_days
    
    def build_snapshot(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        fundamentals: Optional[dict] = None,
        earnings_date: Optional[datetime] = None,
    ) -> StockSnapshot:
        """
        Build a snapshot from price data and fundamentals.
        
        Args:
            symbol: Stock ticker symbol
            price_data: DataFrame with columns [Open, High, Low, Close, Volume]
            fundamentals: Optional dict with PE, market_cap, etc.
            earnings_date: Optional next earnings date
            
        Returns:
            StockSnapshot capturing current state
        """
        if price_data.empty:
            raise ValueError(f"No price data provided for {symbol}")
        
        # Ensure sorted by date
        price_data = price_data.sort_index()
        
        # Calculate indicators
        trend_state, trend_strength = self._calculate_trend(price_data)
        vol_bucket, vol_percentile = self._calculate_volatility(price_data)
        current_price = float(price_data['Close'].iloc[-1])
        vs_52w_high, vs_52w_low = self._calculate_52w_position(price_data)
        
        # Earnings proximity
        days_to_earnings = None
        in_earnings_window = False
        if earnings_date:
            days_to_earnings = (earnings_date - datetime.now()).days
            in_earnings_window = 0 <= days_to_earnings <= 14
        
        # Fundamentals
        pe_ratio = fundamentals.get('pe_ratio') if fundamentals else None
        market_cap = fundamentals.get('market_cap') if fundamentals else None
        fundamental_health = self._assess_fundamental_health(fundamentals)
        
        return StockSnapshot(
            symbol=symbol,
            timestamp=datetime.utcnow(),
            trend_state=trend_state,
            trend_strength=trend_strength,
            volatility_bucket=vol_bucket,
            volatility_percentile=vol_percentile,
            current_price=current_price,
            price_vs_52w_high=vs_52w_high,
            price_vs_52w_low=vs_52w_low,
            days_to_earnings=days_to_earnings,
            in_earnings_window=in_earnings_window,
            pe_ratio=pe_ratio,
            market_cap=market_cap,
            fundamental_health=fundamental_health,
        )
    
    def _calculate_trend(
        self, 
        price_data: pd.DataFrame
    ) -> tuple[TrendState, float]:
        """
        Determine trend state using moving averages.
        
        Simple approach:
        - Compare 20-day MA vs 50-day MA
        - Look at slope of 20-day MA
        """
        close = price_data['Close']
        
        ma_20 = close.rolling(window=20).mean()
        ma_50 = close.rolling(window=50).mean()
        
        if len(close) < 50:
            # Not enough data, use simpler method
            start_price = close.iloc[0]
            end_price = close.iloc[-1]
            change_pct = (end_price - start_price) / start_price * 100
            
            if change_pct > 5:
                return TrendState.UP, min(abs(change_pct) / 20, 1.0)
            elif change_pct < -5:
                return TrendState.DOWN, min(abs(change_pct) / 20, 1.0)
            else:
                return TrendState.SIDEWAYS, 0.3
        
        current_ma20 = ma_20.iloc[-1]
        current_ma50 = ma_50.iloc[-1]
        
        # MA crossover
        ma_diff_pct = (current_ma20 - current_ma50) / current_ma50 * 100
        
        # Slope of MA20 (recent momentum)
        ma20_slope = (ma_20.iloc[-1] - ma_20.iloc[-10]) / ma_20.iloc[-10] * 100
        
        if ma_diff_pct > 2 and ma20_slope > 0:
            strength = min((abs(ma_diff_pct) + abs(ma20_slope)) / 10, 1.0)
            return TrendState.UP, strength
        elif ma_diff_pct < -2 and ma20_slope < 0:
            strength = min((abs(ma_diff_pct) + abs(ma20_slope)) / 10, 1.0)
            return TrendState.DOWN, strength
        else:
            return TrendState.SIDEWAYS, 0.3
    
    def _calculate_volatility(
        self, 
        price_data: pd.DataFrame
    ) -> tuple[VolatilityBucket, float]:
        """
        Calculate volatility bucket using ATR and historical comparison.
        """
        close = price_data['Close']
        high = price_data['High']
        low = price_data['Low']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR as percentage of price
        atr_14 = true_range.rolling(window=14).mean()
        atr_pct = (atr_14 / close * 100).iloc[-1]
        
        # Calculate percentile vs recent history
        atr_pct_series = atr_14 / close * 100
        current_atr_pct = atr_pct_series.iloc[-1]
        percentile = (atr_pct_series < current_atr_pct).sum() / len(atr_pct_series) * 100
        
        # Bucket classification
        if percentile < 25:
            bucket = VolatilityBucket.LOW
        elif percentile > 75:
            bucket = VolatilityBucket.HIGH
        else:
            bucket = VolatilityBucket.NORMAL
        
        return bucket, float(percentile)
    
    def _calculate_52w_position(
        self, 
        price_data: pd.DataFrame
    ) -> tuple[float, float]:
        """Calculate position relative to 52-week high/low."""
        # Use available data (may be less than 52 weeks)
        high_52w = price_data['High'].max()
        low_52w = price_data['Low'].min()
        current = price_data['Close'].iloc[-1]
        
        vs_high = (high_52w - current) / high_52w * 100  # % below high
        vs_low = (current - low_52w) / low_52w * 100     # % above low
        
        return float(vs_high), float(vs_low)
    
    def _assess_fundamental_health(
        self, 
        fundamentals: Optional[dict]
    ) -> FundamentalHealth:
        """
        Simple fundamental health assessment.
        
        This is a basic implementation - can be expanded.
        """
        if not fundamentals:
            return FundamentalHealth.HEALTHY  # Default when no data
        
        pe = fundamentals.get('pe_ratio')
        
        # Very basic rules
        if pe is not None:
            if pe < 0:
                return FundamentalHealth.RISKY  # Negative earnings
            elif pe > 50:
                return FundamentalHealth.WATCH  # Very high valuation
        
        return FundamentalHealth.HEALTHY
