"""Risk analysis - Assess stock risk levels."""

from enum import Enum
from typing import Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel


class RiskLevel(str, Enum):
    """Overall risk classification."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskAnalysisResult(BaseModel):
    """Result of risk analysis."""
    risk_level: RiskLevel
    risk_score: float  # 0-100
    
    # Component scores
    volatility_risk: float  # 0-100
    drawdown_risk: float    # 0-100
    gap_risk: float         # 0-100
    
    # Metrics
    atr_percent: float
    max_drawdown: float
    current_drawdown: float
    avg_gap_percent: float


class RiskAnalyzer:
    """
    Analyzes price data to assess risk levels.
    
    Considers:
    - Volatility (ATR)
    - Drawdown history
    - Gap risk (overnight gaps)
    """
    
    def analyze(self, price_data: pd.DataFrame) -> RiskAnalysisResult:
        """
        Analyze risk from price data.
        
        Args:
            price_data: DataFrame with OHLCV columns
            
        Returns:
            RiskAnalysisResult with risk scores and metrics
        """
        close = price_data['Close']
        high = price_data['High']
        low = price_data['Low']
        open_price = price_data['Open']
        
        # Volatility risk (ATR as % of price)
        atr_pct = self._calculate_atr_percent(high, low, close)
        volatility_risk = self._score_volatility_risk(atr_pct)
        
        # Drawdown risk
        max_dd, current_dd = self._calculate_drawdowns(close)
        drawdown_risk = self._score_drawdown_risk(max_dd, current_dd)
        
        # Gap risk (overnight gaps)
        avg_gap = self._calculate_gap_risk(open_price, close)
        gap_risk = self._score_gap_risk(avg_gap)
        
        # Overall risk score (weighted average)
        risk_score = (
            volatility_risk * 0.4 +
            drawdown_risk * 0.4 +
            gap_risk * 0.2
        )
        
        risk_level = self._classify_risk_level(risk_score)
        
        return RiskAnalysisResult(
            risk_level=risk_level,
            risk_score=float(risk_score),
            volatility_risk=float(volatility_risk),
            drawdown_risk=float(drawdown_risk),
            gap_risk=float(gap_risk),
            atr_percent=float(atr_pct),
            max_drawdown=float(max_dd),
            current_drawdown=float(current_dd),
            avg_gap_percent=float(avg_gap),
        )
    
    def _calculate_atr_percent(
        self, 
        high: pd.Series, 
        low: pd.Series, 
        close: pd.Series,
        period: int = 14
    ) -> float:
        """Calculate ATR as percentage of price."""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = true_range.rolling(window=period).mean().iloc[-1]
        current_price = close.iloc[-1]
        
        return (atr / current_price) * 100
    
    def _calculate_drawdowns(
        self, 
        close: pd.Series
    ) -> tuple[float, float]:
        """Calculate max and current drawdown."""
        rolling_max = close.expanding().max()
        drawdown = (close - rolling_max) / rolling_max * 100
        
        max_drawdown = abs(drawdown.min())
        current_drawdown = abs(drawdown.iloc[-1])
        
        return max_drawdown, current_drawdown
    
    def _calculate_gap_risk(
        self, 
        open_price: pd.Series, 
        close: pd.Series
    ) -> float:
        """Calculate average gap percentage."""
        gaps = abs((open_price - close.shift(1)) / close.shift(1) * 100)
        return gaps.mean()
    
    def _score_volatility_risk(self, atr_pct: float) -> float:
        """Convert ATR% to risk score (0-100)."""
        # ATR% of 1% = low risk, 5%+ = very high risk
        return min(100, atr_pct * 20)
    
    def _score_drawdown_risk(
        self, 
        max_dd: float, 
        current_dd: float
    ) -> float:
        """Convert drawdown to risk score (0-100)."""
        # Weight current drawdown higher
        score = (max_dd * 0.3 + current_dd * 0.7) * 2
        return min(100, score)
    
    def _score_gap_risk(self, avg_gap: float) -> float:
        """Convert average gap to risk score (0-100)."""
        # 0.5% avg gap = moderate, 2%+ = very high
        return min(100, avg_gap * 40)
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify overall risk level from score."""
        if risk_score < 25:
            return RiskLevel.LOW
        elif risk_score < 50:
            return RiskLevel.MODERATE
        elif risk_score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
