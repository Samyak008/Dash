"""Snapshot creation job.

This job runs periodically to:
1. Fetch latest data for portfolio stocks
2. Build new snapshots
3. Store snapshots in database

Runs offline/in background - users never see the process.
"""

from datetime import datetime
from typing import Optional
import logging

from app.data.yahoo import YahooFinanceProvider
from core.snapshots.builder import SnapshotBuilder
from core.snapshots.models import StockSnapshot

logger = logging.getLogger(__name__)


class SnapshotJob:
    """
    Background job for creating stock snapshots.
    
    Design: Heavy intelligence runs offline.
    Users only see clear conclusions.
    """
    
    def __init__(
        self, 
        data_provider: Optional[YahooFinanceProvider] = None,
        snapshot_builder: Optional[SnapshotBuilder] = None
    ):
        self.data_provider = data_provider or YahooFinanceProvider()
        self.snapshot_builder = snapshot_builder or SnapshotBuilder()
    
    async def create_snapshot(self, symbol: str) -> StockSnapshot:
        """
        Create a new snapshot for a single stock.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            New StockSnapshot
        """
        logger.info(f"Creating snapshot for {symbol}")
        
        # Fetch data
        price_data = await self.data_provider.get_price_data(symbol)
        fundamentals_data = await self.data_provider.get_fundamentals(symbol)
        earnings_info = await self.data_provider.get_earnings_info(symbol)
        
        # Convert fundamentals to dict for builder
        fundamentals = {
            'pe_ratio': fundamentals_data.pe_ratio,
            'forward_pe': fundamentals_data.forward_pe,
            'peg_ratio': fundamentals_data.peg_ratio,
            'debt_to_equity': fundamentals_data.debt_to_equity,
            'profit_margin': fundamentals_data.profit_margin,
            'market_cap': fundamentals_data.market_cap,
        }
        
        # Build snapshot
        snapshot = self.snapshot_builder.build_snapshot(
            symbol=symbol,
            price_data=price_data,
            fundamentals=fundamentals,
            earnings_date=earnings_info.next_earnings_date
        )
        
        logger.info(f"Snapshot created for {symbol}: trend={snapshot.trend_state.value}")
        
        return snapshot
    
    async def create_portfolio_snapshots(
        self, 
        symbols: list[str]
    ) -> dict[str, StockSnapshot]:
        """
        Create snapshots for all stocks in a portfolio.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dict mapping symbol to snapshot
        """
        logger.info(f"Creating snapshots for {len(symbols)} stocks")
        
        snapshots = {}
        for symbol in symbols:
            try:
                snapshot = await self.create_snapshot(symbol)
                snapshots[symbol] = snapshot
            except Exception as e:
                logger.error(f"Failed to create snapshot for {symbol}: {e}")
        
        logger.info(f"Created {len(snapshots)}/{len(symbols)} snapshots")
        return snapshots
    
    async def run_scheduled(self):
        """
        Run as scheduled job.
        
        Called by job scheduler (e.g., daily or weekly).
        Fetches all portfolios and creates snapshots.
        """
        logger.info("Running scheduled snapshot job")
        
        # TODO: Get all unique symbols from all portfolios in DB
        # For now, this is a placeholder
        
        # Example workflow:
        # 1. Query DB for all unique symbols across portfolios
        # 2. Create snapshots for each
        # 3. Store in DB
        # 4. Trigger change detection
        
        logger.info("Scheduled snapshot job complete")
