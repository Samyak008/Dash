"""Pydantic schemas for Portfolio validation"""
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from uuid import UUID


class PortfolioBase(BaseModel):
    """Base portfolio schema with common fields"""
    ticker_symbol: str = Field(..., min_length=1, max_length=20)
    quantity: Decimal = Field(..., ge=0, decimal_places=4)
    average_price: Decimal = Field(..., ge=0, decimal_places=2)


class PortfolioCreate(PortfolioBase):
    """Schema for creating a new portfolio entry"""
    pass


class PortfolioResponse(PortfolioBase):
    """Schema for portfolio API responses"""
    id: UUID
    user_id: UUID
    last_synced_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CSVUploadResponse(BaseModel):
    """Response after CSV upload"""
    success: bool
    records_processed: int
    portfolios_created: int
    errors: list[str] = []
