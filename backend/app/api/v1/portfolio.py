"""Portfolio management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4

from app.core.database import get_db
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioResponse, CSVUploadResponse
from app.services.portfolio_parser import PortfolioCSVParser

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_portfolio_csv(
    file: UploadFile = File(...),
    user_id: UUID = None,  # TODO: Get from JWT token after auth is implemented
    db: Session = Depends(get_db)
):
    """
    Upload a portfolio CSV file from Zerodha or Upstox
    
    Corporate Standard: File validation happens before DB writes
    """
    # Temporary: Generate a mock user_id for MVP testing
    # In production, this comes from JWT token
    if user_id is None:
        user_id = uuid4()
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    # Parse CSV
    parser = PortfolioCSVParser(exchange="NSE")
    holdings, errors = parser.parse(content)
    
    if not holdings and errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {'; '.join(errors)}"
        )
    
    # Batch insert/update portfolios
    portfolios_created = 0
    
    for holding in holdings:
        # Check if portfolio entry already exists
        existing = db.query(Portfolio).filter(
            Portfolio.user_id == user_id,
            Portfolio.ticker_symbol == holding.ticker_symbol
        ).first()
        
        if existing:
            # Update existing entry
            existing.quantity = holding.quantity
            existing.average_price = holding.average_price
        else:
            # Create new entry
            portfolio = Portfolio(
                user_id=user_id,
                ticker_symbol=holding.ticker_symbol,
                quantity=holding.quantity,
                average_price=holding.average_price
            )
            db.add(portfolio)
            portfolios_created += 1
    
    db.commit()
    
    return CSVUploadResponse(
        success=True,
        records_processed=len(holdings),
        portfolios_created=portfolios_created,
        errors=errors
    )


@router.get("/", response_model=List[PortfolioResponse])
def get_user_portfolio(
    user_id: UUID = None,  # TODO: Get from JWT
    db: Session = Depends(get_db)
):
    """Get all portfolio holdings for a user"""
    # MVP: For testing, return ALL portfolios if no user_id specified
    # In production, this would come from JWT token and be required
    if user_id is None:
        # Return all portfolios for MVP testing
        portfolios = db.query(Portfolio).all()
    else:
        portfolios = db.query(Portfolio).filter(
            Portfolio.user_id == user_id
        ).all()
    
    return portfolios


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio_entry(
    portfolio: PortfolioCreate,
    user_id: UUID = None,  # TODO: Get from JWT
    db: Session = Depends(get_db)
):
    """Manually add a single portfolio entry"""
    if user_id is None:
        user_id = uuid4()  # Temporary for MVP
    
    # Check for duplicates
    existing = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.ticker_symbol == portfolio.ticker_symbol
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Portfolio entry for {portfolio.ticker_symbol} already exists"
        )
    
    db_portfolio = Portfolio(
        user_id=user_id,
        **portfolio.model_dump()
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    
    return db_portfolio
