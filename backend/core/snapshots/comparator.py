"""Snapshot comparator - Detects changes between snapshots."""

from .models import (
    StockSnapshot,
    SnapshotDiff,
    SnapshotChange,
    ChangeType,
    ChangeSeverity,
    TrendState,
    VolatilityBucket,
)


class SnapshotComparator:
    """
    Compares two snapshots to detect material changes.
    
    Change detection is the core of the system:
    "Did anything meaningful change for this stock since last time?"
    """
    
    # Thresholds for change detection
    TREND_STRENGTH_THRESHOLD = 0.3
    VOLATILITY_CHANGE_THRESHOLD = 30  # percentile points
    PRICE_CHANGE_THRESHOLD = 10  # percent
    
    def compare(
        self, 
        old: StockSnapshot, 
        new: StockSnapshot
    ) -> SnapshotDiff:
        """
        Compare two snapshots and return detected changes.
        
        Args:
            old: Previous snapshot (T0)
            new: Current snapshot (T1)
            
        Returns:
            SnapshotDiff with all detected changes
        """
        if old.symbol != new.symbol:
            raise ValueError("Cannot compare snapshots for different symbols")
        
        changes: list[SnapshotChange] = []
        
        # Check trend changes
        trend_change = self._check_trend_change(old, new)
        if trend_change:
            changes.append(trend_change)
        
        # Check volatility changes
        vol_change = self._check_volatility_change(old, new)
        if vol_change:
            changes.append(vol_change)
        
        # Check earnings proximity
        earnings_change = self._check_earnings_change(old, new)
        if earnings_change:
            changes.append(earnings_change)
        
        # Check fundamental changes
        fundamental_change = self._check_fundamental_change(old, new)
        if fundamental_change:
            changes.append(fundamental_change)
        
        # Check price breakouts
        price_change = self._check_price_change(old, new)
        if price_change:
            changes.append(price_change)
        
        # Determine overall severity and summary
        has_material_change = len(changes) > 0
        overall_severity = self._calculate_overall_severity(changes)
        summary = self._generate_summary(new.symbol, changes)
        
        # Status change
        status_changed = old.fundamental_health != new.fundamental_health
        
        return SnapshotDiff(
            symbol=new.symbol,
            from_timestamp=old.timestamp,
            to_timestamp=new.timestamp,
            changes=changes,
            has_material_change=has_material_change,
            overall_severity=overall_severity,
            summary=summary,
            status_changed=status_changed,
            old_status=old.fundamental_health,
            new_status=new.fundamental_health,
        )
    
    def _check_trend_change(
        self, 
        old: StockSnapshot, 
        new: StockSnapshot
    ) -> SnapshotChange | None:
        """Detect trend reversals."""
        if old.trend_state != new.trend_state:
            # Trend reversal detected
            severity = ChangeSeverity.HIGH
            
            # Up -> Down is more severe
            if old.trend_state == TrendState.UP and new.trend_state == TrendState.DOWN:
                severity = ChangeSeverity.CRITICAL
            
            return SnapshotChange(
                change_type=ChangeType.TREND_REVERSAL,
                severity=severity,
                description=f"Trend changed from {old.trend_state.value} to {new.trend_state.value}",
                old_value=old.trend_state.value,
                new_value=new.trend_state.value,
            )
        
        return None
    
    def _check_volatility_change(
        self, 
        old: StockSnapshot, 
        new: StockSnapshot
    ) -> SnapshotChange | None:
        """Detect significant volatility changes."""
        vol_change = new.volatility_percentile - old.volatility_percentile
        
        if abs(vol_change) >= self.VOLATILITY_CHANGE_THRESHOLD:
            if vol_change > 0:
                return SnapshotChange(
                    change_type=ChangeType.VOLATILITY_SPIKE,
                    severity=ChangeSeverity.MEDIUM if vol_change < 40 else ChangeSeverity.HIGH,
                    description=f"Volatility increased significantly ({vol_change:.0f} percentile points)",
                    old_value=f"{old.volatility_percentile:.0f}th percentile",
                    new_value=f"{new.volatility_percentile:.0f}th percentile",
                )
            else:
                return SnapshotChange(
                    change_type=ChangeType.VOLATILITY_DROP,
                    severity=ChangeSeverity.LOW,
                    description=f"Volatility decreased ({abs(vol_change):.0f} percentile points)",
                    old_value=f"{old.volatility_percentile:.0f}th percentile",
                    new_value=f"{new.volatility_percentile:.0f}th percentile",
                )
        
        return None
    
    def _check_earnings_change(
        self, 
        old: StockSnapshot, 
        new: StockSnapshot
    ) -> SnapshotChange | None:
        """Detect when entering earnings window."""
        if not old.in_earnings_window and new.in_earnings_window:
            return SnapshotChange(
                change_type=ChangeType.EARNINGS_APPROACHING,
                severity=ChangeSeverity.MEDIUM,
                description=f"Entering earnings window (report in {new.days_to_earnings} days)",
                old_value="outside earnings window",
                new_value=f"{new.days_to_earnings} days to earnings",
            )
        
        return None
    
    def _check_fundamental_change(
        self, 
        old: StockSnapshot, 
        new: StockSnapshot
    ) -> SnapshotChange | None:
        """Detect fundamental health changes."""
        if old.fundamental_health != new.fundamental_health:
            # Determine severity based on direction
            severity = ChangeSeverity.MEDIUM
            
            if new.fundamental_health.value == "risky":
                severity = ChangeSeverity.CRITICAL
            elif old.fundamental_health.value == "risky":
                severity = ChangeSeverity.HIGH  # Improvement from risky
            
            return SnapshotChange(
                change_type=ChangeType.FUNDAMENTAL_SHIFT,
                severity=severity,
                description=f"Fundamental health changed from {old.fundamental_health.value} to {new.fundamental_health.value}",
                old_value=old.fundamental_health.value,
                new_value=new.fundamental_health.value,
            )
        
        return None
    
    def _check_price_change(
        self, 
        old: StockSnapshot, 
        new: StockSnapshot
    ) -> SnapshotChange | None:
        """Detect significant price breakouts or breakdowns."""
        price_change_pct = (new.current_price - old.current_price) / old.current_price * 100
        
        if price_change_pct >= self.PRICE_CHANGE_THRESHOLD:
            return SnapshotChange(
                change_type=ChangeType.PRICE_BREAKOUT,
                severity=ChangeSeverity.HIGH,
                description=f"Price broke out +{price_change_pct:.1f}%",
                old_value=f"${old.current_price:.2f}",
                new_value=f"${new.current_price:.2f}",
            )
        elif price_change_pct <= -self.PRICE_CHANGE_THRESHOLD:
            return SnapshotChange(
                change_type=ChangeType.PRICE_BREAKDOWN,
                severity=ChangeSeverity.CRITICAL,
                description=f"Price broke down {price_change_pct:.1f}%",
                old_value=f"${old.current_price:.2f}",
                new_value=f"${new.current_price:.2f}",
            )
        
        return None
    
    def _calculate_overall_severity(
        self, 
        changes: list[SnapshotChange]
    ) -> ChangeSeverity:
        """Calculate overall severity from list of changes."""
        if not changes:
            return ChangeSeverity.LOW
        
        severity_order = [
            ChangeSeverity.LOW,
            ChangeSeverity.MEDIUM,
            ChangeSeverity.HIGH,
            ChangeSeverity.CRITICAL,
        ]
        
        max_severity = ChangeSeverity.LOW
        for change in changes:
            if severity_order.index(change.severity) > severity_order.index(max_severity):
                max_severity = change.severity
        
        return max_severity
    
    def _generate_summary(
        self, 
        symbol: str, 
        changes: list[SnapshotChange]
    ) -> str:
        """Generate human-readable summary of changes."""
        if not changes:
            return f"No material changes detected for {symbol}"
        
        if len(changes) == 1:
            return f"{symbol}: {changes[0].description}"
        
        summaries = [c.description for c in changes[:3]]  # Top 3
        return f"{symbol}: {'; '.join(summaries)}"
