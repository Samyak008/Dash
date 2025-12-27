"""Prompt templates for LLM-based insights.

LLMs are used for:
- Thesis generation
- Explanation of changes
- Bull/Bear reasoning

LLMs should NEVER see:
- Raw OHLC data
- Technical indicator calculations

They only receive pre-computed analysis results.
"""

# Change explanation prompt
EXPLAIN_CHANGE_PROMPT = """You are a calm, professional stock analyst explaining a change to a retail investor.

Stock: {symbol}
Change Detected: {change_type}
Severity: {severity}

Before State:
- Trend: {old_trend}
- Volatility: {old_volatility}  
- Status: {old_status}

After State:
- Trend: {new_trend}
- Volatility: {new_volatility}
- Status: {new_status}

Price Context:
- Current price: ${current_price}
- vs 52-week high: {vs_52w_high}% below
- vs 52-week low: {vs_52w_low}% above

Your task:
1. Explain what changed in 1-2 sentences
2. Explain why this matters in 1-2 sentences
3. Provide one key thing to watch (invalidation signal)

Be calm and factual. No alarmism. No buy/sell recommendations.
"""


# Weekly summary prompt
WEEKLY_SUMMARY_PROMPT = """You are creating a weekly portfolio summary for a retail investor.

Portfolio: {portfolio_name}
Period: {week_start} to {week_end}
Total Holdings: {total_holdings}

Changes This Week:
{changes_summary}

Stocks with Changes:
{stocks_changed}

Stocks Unchanged:
{stocks_unchanged}

Create a brief, calm summary that:
1. Highlights the most important change (if any)
2. Notes any stocks that need attention
3. Reassures on stocks that are stable
4. Lists 2-3 things to watch next week

Tone: Professional, calm, trustworthy. Like a good financial advisor.
No predictions. No buy/sell. Just clarity on what changed.
"""


# Thesis generation prompt  
GENERATE_THESIS_PROMPT = """You are generating an investment thesis summary for a stock.

Stock: {symbol}
Company: {company_name}
Sector: {sector}

Current Analysis:
- Trend: {trend_direction} (strength: {trend_strength})
- Risk Level: {risk_level}
- Fundamental Health: {fundamental_health}
- Valuation: {valuation}

Context:
- Price vs 52w High: {vs_52w_high}%
- Price vs 52w Low: {vs_52w_low}%
- Days to Earnings: {days_to_earnings}

Generate a brief thesis with:
1. Bull Case (2-3 sentences): What would have to go right
2. Bear Case (2-3 sentences): What could go wrong
3. Key Risk: The single biggest risk to watch
4. Invalidation: What would prove this thesis wrong

Be balanced. No recommendations. Just analysis.
"""


class InsightPrompts:
    """Prompt template manager."""
    
    EXPLAIN_CHANGE = EXPLAIN_CHANGE_PROMPT
    WEEKLY_SUMMARY = WEEKLY_SUMMARY_PROMPT
    GENERATE_THESIS = GENERATE_THESIS_PROMPT
    
    @staticmethod
    def format_change_explanation(
        symbol: str,
        change_type: str,
        severity: str,
        old_state: dict,
        new_state: dict,
        price_context: dict
    ) -> str:
        """Format the change explanation prompt."""
        return EXPLAIN_CHANGE_PROMPT.format(
            symbol=symbol,
            change_type=change_type,
            severity=severity,
            old_trend=old_state.get('trend', 'unknown'),
            old_volatility=old_state.get('volatility', 'unknown'),
            old_status=old_state.get('status', 'unknown'),
            new_trend=new_state.get('trend', 'unknown'),
            new_volatility=new_state.get('volatility', 'unknown'),
            new_status=new_state.get('status', 'unknown'),
            current_price=price_context.get('price', 0),
            vs_52w_high=price_context.get('vs_52w_high', 0),
            vs_52w_low=price_context.get('vs_52w_low', 0)
        )
    
    @staticmethod
    def format_weekly_summary(
        portfolio_name: str,
        week_start: str,
        week_end: str,
        total_holdings: int,
        changes_summary: str,
        stocks_changed: list[str],
        stocks_unchanged: list[str]
    ) -> str:
        """Format the weekly summary prompt."""
        return WEEKLY_SUMMARY_PROMPT.format(
            portfolio_name=portfolio_name,
            week_start=week_start,
            week_end=week_end,
            total_holdings=total_holdings,
            changes_summary=changes_summary,
            stocks_changed=", ".join(stocks_changed) if stocks_changed else "None",
            stocks_unchanged=", ".join(stocks_unchanged) if stocks_unchanged else "None"
        )
