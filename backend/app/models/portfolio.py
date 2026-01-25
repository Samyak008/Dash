"""Portfolio database model"""
from sqlalchemy import Column, String, DateTime, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Portfolio(Base):
    """User portfolio holdings - tracks what stocks users own"""
    
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    
    # Ticker with exchange suffix (e.g., RELIANCE.NS for NSE, RELIANCE.BO for BSE)
    ticker_symbol = Column(String(20), nullable=False, index=True)
    
    # Financial data - Numeric(precision, scale) is standard for money/quantities
    quantity = Column(Numeric(18, 4), nullable=False, default=0)
    average_price = Column(Numeric(18, 2), nullable=False, default=0)
    
    # Metadata
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite index for efficient user+ticker lookups
    __table_args__ = (
        Index('idx_user_ticker', 'user_id', 'ticker_symbol'),
    )

    def __repr__(self):
        return f"<Portfolio {self.ticker_symbol} qty={self.quantity}>"
