"""Trend analysis - Determine stock trend state."""

from enum import Enum
from typing import Optional
import pandas as pd
from pydantic import BaseModel


class TrendDirection(str, Enum):
    """Trend direction classification."""
    STRONG_UP = "strong_up"
    UP = "up"
    SIDEWAYS = "sideways"
    DOWN = "down"
    STRONG_DOWN = "strong_down"


class TrendAnalysisResult(BaseModel):
    """Result of trend analysis."""
    direction: TrendDirection
    strength: float  # 0-1
    ma_20: float
    ma_50: float
    ma_200: Optional[float] = None
    above_ma_20: bool
    above_ma_50: bool
    above_ma_200: Optional[bool] = None
    momentum_score: float  # -1 to 1


class TrendAnalyzer:
    """
    Analyzes price data to determine trend state.
    
    Uses moving averages and momentum indicators.
    No ML - purely deterministic rules.
    """
    
    def analyze(self, price_data: pd.DataFrame) -> TrendAnalysisResult:
        """
        Analyze trend from price data.
        
        Args:
            price_data: DataFrame with OHLCV columns
            
        Returns:
            TrendAnalysisResult with direction and metrics
        """
        close = price_data['Close']
        
        # Calculate moving averages
        ma_20 = close.rolling(window=20).mean()
        ma_50 = close.rolling(window=50).mean()
        ma_200 = close.rolling(window=200).mean() if len(close) >= 200 else None
        
        current_price = close.iloc[-1]
        current_ma_20 = ma_20.iloc[-1]
        current_ma_50 = ma_50.iloc[-1]
        current_ma_200 = ma_200.iloc[-1] if ma_200 is not None else None
        
        # Price vs MAs
        above_ma_20 = current_price > current_ma_20
        above_ma_50 = current_price > current_ma_50
        above_ma_200 = current_price > current_ma_200 if current_ma_200 else None
        
        # Momentum (rate of change)
        roc_10 = (current_price - close.iloc[-10]) / close.iloc[-10] if len(close) >= 10 else 0
        roc_20 = (current_price - close.iloc[-20]) / close.iloc[-20] if len(close) >= 20 else 0
        momentum_score = (roc_10 + roc_20) / 2
        momentum_score = max(-1, min(1, momentum_score * 10))  # Normalize to -1 to 1
        
        # Determine direction and strength
        direction, strength = self._classify_trend(
            above_ma_20, above_ma_50, above_ma_200,
            current_ma_20, current_ma_50, momentum_score
        )
        
        return TrendAnalysisResult(
            direction=direction,
            strength=strength,
            ma_20=float(current_ma_20),
            ma_50=float(current_ma_50),
            ma_200=float(current_ma_200) if current_ma_200 else None,
            above_ma_20=above_ma_20,
            above_ma_50=above_ma_50,
            above_ma_200=above_ma_200,
            momentum_score=float(momentum_score),
        )
    
    def _classify_trend(
        self,
        above_ma_20: bool,
        above_ma_50: bool,
        above_ma_200: Optional[bool],
        ma_20: float,
        ma_50: float,
        momentum: float,
    ) -> tuple[TrendDirection, float]:
        """Classify trend direction and strength."""
        
        # Count bullish signals
        bullish_signals = sum([
            above_ma_20,
            above_ma_50,
            above_ma_200 if above_ma_200 is not None else False,
            ma_20 > ma_50,
            momentum > 0.2,
        ])
        
        bearish_signals = sum([
            not above_ma_20,
            not above_ma_50,
            not above_ma_200 if above_ma_200 is not None else False,
            ma_20 < ma_50,
            momentum < -0.2,
        ])
        
        total_signals = 5 if above_ma_200 is not None else 4
        
        if bullish_signals >= 4:
            return TrendDirection.STRONG_UP, bullish_signals / total_signals
        elif bullish_signals >= 3:
            return TrendDirection.UP, bullish_signals / total_signals
        elif bearish_signals >= 4:
            return TrendDirection.STRONG_DOWN, bearish_signals / total_signals
        elif bearish_signals >= 3:
            return TrendDirection.DOWN, bearish_signals / total_signals
        else:
            return TrendDirection.SIDEWAYS, 0.5
