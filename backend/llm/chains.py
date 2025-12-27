"""LLM chains for generating insights.

These chains orchestrate LLM calls to generate:
- Change explanations
- Weekly summaries
- Investment theses

Currently a placeholder - will integrate with LangChain.
"""

from typing import Optional
from pydantic import BaseModel

from .prompts import InsightPrompts


class ChangeExplanation(BaseModel):
    """Generated explanation for a change."""
    what_changed: str
    why_it_matters: str
    what_to_watch: str


class WeeklySummary(BaseModel):
    """Generated weekly summary."""
    summary: str
    top_concerns: list[str]
    watch_items: list[str]


class StockThesis(BaseModel):
    """Generated investment thesis."""
    bull_case: str
    bear_case: str
    key_risk: str
    invalidation: str


class InsightChain:
    """
    Chain for generating insights using LLMs.
    
    This is a placeholder that returns mock data.
    Will be implemented with LangChain when ready.
    
    Design principle: LLMs only see analysis results,
    never raw price data or indicator calculations.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        # TODO: Initialize LangChain LLM
        self._llm = None
    
    async def explain_change(
        self,
        symbol: str,
        change_type: str,
        severity: str,
        old_state: dict,
        new_state: dict,
        price_context: dict
    ) -> ChangeExplanation:
        """
        Generate explanation for a detected change.
        
        Args:
            symbol: Stock ticker
            change_type: Type of change detected
            severity: Change severity
            old_state: Previous state dict
            new_state: Current state dict
            price_context: Price context dict
            
        Returns:
            ChangeExplanation with what/why/watch
        """
        # TODO: Implement with LangChain
        # For now, return a template response
        
        prompt = InsightPrompts.format_change_explanation(
            symbol=symbol,
            change_type=change_type,
            severity=severity,
            old_state=old_state,
            new_state=new_state,
            price_context=price_context
        )
        
        # Mock response - replace with actual LLM call
        return ChangeExplanation(
            what_changed=f"{symbol} trend changed from {old_state.get('trend', 'unknown')} to {new_state.get('trend', 'unknown')}",
            why_it_matters="This shift suggests a change in investor sentiment and may indicate a new price direction.",
            what_to_watch=f"Watch for price to hold above the 20-day moving average to confirm the trend."
        )
    
    async def generate_weekly_summary(
        self,
        portfolio_name: str,
        holdings: list[dict],
        changes: list[dict]
    ) -> WeeklySummary:
        """
        Generate weekly portfolio summary.
        
        Args:
            portfolio_name: Name of portfolio
            holdings: List of holdings with status
            changes: List of changes detected this week
            
        Returns:
            WeeklySummary with narrative
        """
        # TODO: Implement with LangChain
        
        stocks_with_changes = [c['symbol'] for c in changes]
        stocks_unchanged = [h['symbol'] for h in holdings if h['symbol'] not in stocks_with_changes]
        
        # Mock response
        return WeeklySummary(
            summary=f"Your portfolio had {len(changes)} notable changes this week. "
                   f"Most holdings remain stable.",
            top_concerns=[f"{c['symbol']}: {c.get('description', 'change detected')}" for c in changes[:2]],
            watch_items=["Check any upcoming earnings dates", "Monitor overall market sentiment"]
        )
    
    async def generate_thesis(
        self,
        symbol: str,
        company_name: str,
        analysis: dict
    ) -> StockThesis:
        """
        Generate investment thesis for a stock.
        
        Args:
            symbol: Stock ticker
            company_name: Company name
            analysis: Analysis results dict
            
        Returns:
            StockThesis with bull/bear cases
        """
        # TODO: Implement with LangChain
        
        # Mock response
        return StockThesis(
            bull_case=f"{symbol} shows positive momentum with healthy fundamentals. "
                     "Continued market strength could drive further gains.",
            bear_case="Elevated valuation and market uncertainty pose risks. "
                     "Any earnings miss could trigger a pullback.",
            key_risk="Valuation compression if growth slows",
            invalidation="A sustained break below the 50-day moving average would invalidate the bullish thesis."
        )
