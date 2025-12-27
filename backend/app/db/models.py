"""Database models for the Stock Intelligence Platform."""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolios: Mapped[list["Portfolio"]] = relationship("Portfolio", back_populates="user")


class Portfolio(Base):
    """User portfolio model."""
    
    __tablename__ = "portfolios"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="portfolios")
    stocks: Mapped[list["PortfolioStock"]] = relationship("PortfolioStock", back_populates="portfolio")


class PortfolioStock(Base):
    """Stock holding in a portfolio."""
    
    __tablename__ = "portfolio_stocks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    portfolio_id: Mapped[str] = mapped_column(String(36), ForeignKey("portfolios.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    shares: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    avg_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="stocks")


class Snapshot(Base):
    """Stock state snapshot for change detection."""
    
    __tablename__ = "snapshots"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Trend state
    trend_state: Mapped[str] = mapped_column(String(20), nullable=False)  # up, down, sideways
    trend_strength: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Volatility
    volatility_bucket: Mapped[str] = mapped_column(String(20), nullable=False)  # low, normal, high
    volatility_percentile: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Price context
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    price_vs_52w_high: Mapped[float] = mapped_column(Float, nullable=False)
    price_vs_52w_low: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Events
    days_to_earnings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    in_earnings_window: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Fundamentals
    pe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    market_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fundamental_health: Mapped[str] = mapped_column(String(20), default="healthy")
    
    # Full snapshot data as JSON (for flexibility)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class Insight(Base):
    """Generated insight from change detection."""
    
    __tablename__ = "insights"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Change info
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # trend_change, volatility_change, etc.
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high, critical
    
    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    significance: Mapped[str] = mapped_column(Text, nullable=False)
    invalidation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Context
    old_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Snapshot references
    from_snapshot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("snapshots.id"), nullable=True)
    to_snapshot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("snapshots.id"), nullable=True)
    
    # User interaction
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
