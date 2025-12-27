"""Fundamental analysis - Assess company fundamentals."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ValuationLevel(str, Enum):
    """Valuation classification."""
    UNDERVALUED = "undervalued"
    FAIR = "fair"
    OVERVALUED = "overvalued"
    VERY_OVERVALUED = "very_overvalued"


class FundamentalHealth(str, Enum):
    """Overall fundamental health."""
    STRONG = "strong"
    HEALTHY = "healthy"
    WATCH = "watch"
    WEAK = "weak"


class FundamentalAnalysisResult(BaseModel):
    """Result of fundamental analysis."""
    health: FundamentalHealth
    health_score: float  # 0-100
    valuation: ValuationLevel
    
    # Metrics
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    debt_to_equity: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_growth: Optional[float] = None
    
    # Flags
    profitable: bool = True
    positive_growth: bool = True
    reasonable_debt: bool = True


class FundamentalAnalyzer:
    """
    Analyzes company fundamentals.
    
    Uses basic metrics like P/E, PEG, debt ratios.
    No complex financial modeling - simple health checks.
    """
    
    def analyze(self, fundamentals: dict) -> FundamentalAnalysisResult:
        """
        Analyze fundamentals from data dict.
        
        Args:
            fundamentals: Dict with fundamental metrics
            
        Returns:
            FundamentalAnalysisResult with health assessment
        """
        # Extract metrics
        pe = fundamentals.get('pe_ratio')
        forward_pe = fundamentals.get('forward_pe')
        peg = fundamentals.get('peg_ratio')
        pb = fundamentals.get('price_to_book')
        de = fundamentals.get('debt_to_equity')
        margin = fundamentals.get('profit_margin')
        growth = fundamentals.get('revenue_growth')
        
        # Assess flags
        profitable = pe is None or pe > 0
        positive_growth = growth is None or growth > 0
        reasonable_debt = de is None or de < 2.0
        
        # Calculate valuation
        valuation = self._assess_valuation(pe, forward_pe, peg)
        
        # Calculate health score
        health_score = self._calculate_health_score(
            pe, forward_pe, peg, de, margin, growth,
            profitable, positive_growth, reasonable_debt
        )
        
        health = self._classify_health(health_score)
        
        return FundamentalAnalysisResult(
            health=health,
            health_score=health_score,
            valuation=valuation,
            pe_ratio=pe,
            forward_pe=forward_pe,
            peg_ratio=peg,
            price_to_book=pb,
            debt_to_equity=de,
            profit_margin=margin,
            revenue_growth=growth,
            profitable=profitable,
            positive_growth=positive_growth,
            reasonable_debt=reasonable_debt,
        )
    
    def _assess_valuation(
        self,
        pe: Optional[float],
        forward_pe: Optional[float],
        peg: Optional[float],
    ) -> ValuationLevel:
        """Assess valuation level from multiples."""
        if pe is None and forward_pe is None:
            return ValuationLevel.FAIR  # Can't assess
        
        # Use PEG if available (best metric)
        if peg is not None:
            if peg < 1.0:
                return ValuationLevel.UNDERVALUED
            elif peg < 2.0:
                return ValuationLevel.FAIR
            elif peg < 3.0:
                return ValuationLevel.OVERVALUED
            else:
                return ValuationLevel.VERY_OVERVALUED
        
        # Fall back to P/E
        check_pe = forward_pe if forward_pe else pe
        if check_pe:
            if check_pe < 0:
                return ValuationLevel.OVERVALUED  # Negative earnings
            elif check_pe < 15:
                return ValuationLevel.UNDERVALUED
            elif check_pe < 25:
                return ValuationLevel.FAIR
            elif check_pe < 40:
                return ValuationLevel.OVERVALUED
            else:
                return ValuationLevel.VERY_OVERVALUED
        
        return ValuationLevel.FAIR
    
    def _calculate_health_score(
        self,
        pe: Optional[float],
        forward_pe: Optional[float],
        peg: Optional[float],
        de: Optional[float],
        margin: Optional[float],
        growth: Optional[float],
        profitable: bool,
        positive_growth: bool,
        reasonable_debt: bool,
    ) -> float:
        """Calculate overall health score (0-100)."""
        score = 50  # Start at neutral
        
        # Profitability bonus/penalty
        if profitable:
            score += 15
        else:
            score -= 25
        
        # Growth bonus/penalty
        if positive_growth:
            score += 10
            if growth and growth > 0.1:  # >10% growth
                score += 10
        else:
            score -= 15
        
        # Debt penalty
        if reasonable_debt:
            score += 5
        else:
            score -= 20
        
        # Margin bonus
        if margin and margin > 0.15:  # >15% margin
            score += 10
        
        # Valuation adjustment
        if peg and peg < 1.5:
            score += 10
        elif pe and 0 < pe < 20:
            score += 5
        
        return max(0, min(100, score))
    
    def _classify_health(self, score: float) -> FundamentalHealth:
        """Classify health from score."""
        if score >= 75:
            return FundamentalHealth.STRONG
        elif score >= 55:
            return FundamentalHealth.HEALTHY
        elif score >= 35:
            return FundamentalHealth.WATCH
        else:
            return FundamentalHealth.WEAK
