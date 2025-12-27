"""Yahoo Finance data provider."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import yfinance as yf
from pydantic import BaseModel

from app.config import get_settings


class StockQuote(BaseModel):
    """Current stock quote."""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    timestamp: datetime


class StockFundamentals(BaseModel):
    """Fundamental data for a stock."""
    symbol: str
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    debt_to_equity: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_growth: Optional[float] = None
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    name: Optional[str] = None


class EarningsInfo(BaseModel):
    """Earnings date information."""
    symbol: str
    next_earnings_date: Optional[datetime] = None
    days_until_earnings: Optional[int] = None


class YahooFinanceProvider:
    """
    Yahoo Finance data provider.
    
    Fetches price data, fundamentals, and earnings info.
    Uses yfinance library.
    
    Note: Only fetch 60-90 days of data as per plan.
    Do NOT store full historical data.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._rate_limit_delay = self.settings.yahoo_rate_limit_delay
    
    async def get_price_data(
        self, 
        symbol: str, 
        days: int = 90
    ) -> pd.DataFrame:
        """
        Get recent price data for a stock.
        
        Args:
            symbol: Stock ticker symbol
            days: Number of days of history (default 90)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._fetch_price_data, 
            symbol, 
            days
        )
    
    def _fetch_price_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Synchronous price data fetch."""
        ticker = yf.Ticker(symbol)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = ticker.history(start=start_date, end=end_date)
        
        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column {col} in price data")
        
        return df[required_cols]
    
    async def get_quote(self, symbol: str) -> StockQuote:
        """
        Get current quote for a stock.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._fetch_quote, 
            symbol
        )
    
    def _fetch_quote(self, symbol: str) -> StockQuote:
        """Synchronous quote fetch."""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        price = info.get('regularMarketPrice', info.get('currentPrice', 0))
        prev_close = info.get('regularMarketPreviousClose', price)
        change = price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        return StockQuote(
            symbol=symbol.upper(),
            price=price,
            change=change,
            change_percent=change_pct,
            volume=info.get('regularMarketVolume', 0),
            market_cap=info.get('marketCap'),
            timestamp=datetime.utcnow()
        )
    
    async def get_fundamentals(self, symbol: str) -> StockFundamentals:
        """
        Get fundamental data for a stock.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._fetch_fundamentals, 
            symbol
        )
    
    def _fetch_fundamentals(self, symbol: str) -> StockFundamentals:
        """Synchronous fundamentals fetch."""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return StockFundamentals(
            symbol=symbol.upper(),
            pe_ratio=info.get('trailingPE'),
            forward_pe=info.get('forwardPE'),
            peg_ratio=info.get('pegRatio'),
            price_to_book=info.get('priceToBook'),
            debt_to_equity=info.get('debtToEquity'),
            profit_margin=info.get('profitMargins'),
            revenue_growth=info.get('revenueGrowth'),
            market_cap=info.get('marketCap'),
            sector=info.get('sector'),
            industry=info.get('industry'),
            name=info.get('shortName', info.get('longName'))
        )
    
    async def get_earnings_info(self, symbol: str) -> EarningsInfo:
        """
        Get next earnings date for a stock.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._fetch_earnings_info, 
            symbol
        )
    
    def _fetch_earnings_info(self, symbol: str) -> EarningsInfo:
        """Synchronous earnings info fetch."""
        ticker = yf.Ticker(symbol)
        
        # Try to get earnings dates
        try:
            calendar = ticker.calendar
            if calendar is not None and 'Earnings Date' in calendar:
                earnings_dates = calendar['Earnings Date']
                if earnings_dates:
                    next_date = earnings_dates[0]
                    if isinstance(next_date, datetime):
                        days_until = (next_date - datetime.now()).days
                        return EarningsInfo(
                            symbol=symbol.upper(),
                            next_earnings_date=next_date,
                            days_until_earnings=days_until
                        )
        except Exception:
            pass
        
        return EarningsInfo(
            symbol=symbol.upper(),
            next_earnings_date=None,
            days_until_earnings=None
        )
    
    async def search_symbols(self, query: str) -> list[dict]:
        """
        Search for stock symbols.
        
        Note: yfinance doesn't have great search.
        This is a basic implementation.
        """
        # For now, just validate the symbol
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info.get('shortName'):
                return [{
                    'symbol': query.upper(),
                    'name': info.get('shortName', info.get('longName', query))
                }]
        except Exception:
            pass
        
        return []
