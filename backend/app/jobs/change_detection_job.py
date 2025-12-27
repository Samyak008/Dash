"""Change detection job.

This job runs after snapshots are created to:
1. Compare new snapshots with previous ones
2. Detect material changes
3. Generate insights
4. Store alerts/notifications

Core feature: Answer "Did anything meaningful change?"
"""

from datetime import datetime
from typing import Optional
import logging

from core.snapshots.comparator import SnapshotComparator
from core.snapshots.models import StockSnapshot, SnapshotDiff, ChangeSeverity

logger = logging.getLogger(__name__)


class ChangeDetectionJob:
    """
    Background job for detecting changes between snapshots.
    
    This is the core of Feature #1: Material Change Detection.
    
    Change = Snapshot_T1 - Snapshot_T0
    No ML needed - purely deterministic comparison.
    """
    
    def __init__(self, comparator: Optional[SnapshotComparator] = None):
        self.comparator = comparator or SnapshotComparator()
    
    async def detect_changes(
        self, 
        old_snapshot: StockSnapshot, 
        new_snapshot: StockSnapshot
    ) -> SnapshotDiff:
        """
        Detect changes between two snapshots.
        
        Args:
            old_snapshot: Previous snapshot (T0)
            new_snapshot: Current snapshot (T1)
            
        Returns:
            SnapshotDiff with detected changes
        """
        logger.info(f"Detecting changes for {new_snapshot.symbol}")
        
        diff = self.comparator.compare(old_snapshot, new_snapshot)
        
        if diff.has_material_change:
            logger.info(
                f"Material change detected for {new_snapshot.symbol}: "
                f"{diff.overall_severity.value} - {len(diff.changes)} changes"
            )
        else:
            logger.debug(f"No material changes for {new_snapshot.symbol}")
        
        return diff
    
    async def detect_portfolio_changes(
        self,
        old_snapshots: dict[str, StockSnapshot],
        new_snapshots: dict[str, StockSnapshot]
    ) -> dict[str, SnapshotDiff]:
        """
        Detect changes for all stocks in a portfolio.
        
        Args:
            old_snapshots: Previous snapshots by symbol
            new_snapshots: Current snapshots by symbol
            
        Returns:
            Dict mapping symbol to SnapshotDiff
        """
        logger.info(f"Detecting changes for {len(new_snapshots)} stocks")
        
        diffs = {}
        for symbol, new_snapshot in new_snapshots.items():
            old_snapshot = old_snapshots.get(symbol)
            if old_snapshot:
                try:
                    diff = await self.detect_changes(old_snapshot, new_snapshot)
                    diffs[symbol] = diff
                except Exception as e:
                    logger.error(f"Failed to compare snapshots for {symbol}: {e}")
            else:
                logger.info(f"No previous snapshot for {symbol} - first snapshot")
        
        # Summary
        material_changes = sum(1 for d in diffs.values() if d.has_material_change)
        logger.info(f"Found {material_changes}/{len(diffs)} stocks with material changes")
        
        return diffs
    
    def filter_significant_changes(
        self, 
        diffs: dict[str, SnapshotDiff],
        min_severity: ChangeSeverity = ChangeSeverity.MEDIUM
    ) -> dict[str, SnapshotDiff]:
        """
        Filter to only significant changes.
        
        Args:
            diffs: All detected diffs
            min_severity: Minimum severity to include
            
        Returns:
            Filtered diffs
        """
        severity_order = [
            ChangeSeverity.LOW,
            ChangeSeverity.MEDIUM,
            ChangeSeverity.HIGH,
            ChangeSeverity.CRITICAL,
        ]
        
        min_index = severity_order.index(min_severity)
        
        return {
            symbol: diff
            for symbol, diff in diffs.items()
            if diff.has_material_change 
            and severity_order.index(diff.overall_severity) >= min_index
        }
    
    async def run_scheduled(self):
        """
        Run as scheduled job after snapshot job.
        
        Workflow:
        1. For each portfolio, get old and new snapshots
        2. Detect changes
        3. Generate insights for significant changes
        4. Store insights and trigger notifications
        """
        logger.info("Running scheduled change detection job")
        
        # TODO: Implement full workflow
        # 1. Query portfolios from DB
        # 2. Get old/new snapshots for each
        # 3. Run detection
        # 4. Generate insights (LLM)
        # 5. Store and notify
        
        logger.info("Scheduled change detection job complete")
    
    def summarize_changes(self, diffs: dict[str, SnapshotDiff]) -> dict:
        """
        Create summary of all changes.
        
        Returns summary suitable for weekly report.
        """
        total_stocks = len(diffs)
        stocks_with_changes = sum(1 for d in diffs.values() if d.has_material_change)
        
        by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for symbol, diff in diffs.items():
            if diff.has_material_change:
                by_severity[diff.overall_severity.value].append({
                    'symbol': symbol,
                    'summary': diff.summary,
                    'changes': len(diff.changes)
                })
        
        return {
            'total_stocks': total_stocks,
            'stocks_with_changes': stocks_with_changes,
            'stocks_unchanged': total_stocks - stocks_with_changes,
            'by_severity': by_severity,
            'top_concerns': (
                by_severity['critical'] + by_severity['high']
            )[:5]  # Top 5 concerns
        }
