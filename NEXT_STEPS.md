# Dash Backend - Setup Complete 

## What We Built

### Corporate-Grade Backend Foundation
**Project Structure** - Organized following enterprise best practices  
**Database Models** - Portfolio table with proper typing (Numeric for financial data)  
**Pydantic Schemas** - Full validation for all API inputs/outputs  
**CSV Parser** - Smart broker detection (Zerodha/Upstox) with error handling  
**FastAPI Routes** - RESTful endpoints for portfolio management  
**Alembic Migrations** - Version-controlled database schema  
**Configuration** - Environment-based settings with Pydantic  

---

##  Network Issue Detected

The migration failed due to **network connectivity to Supabase**:
```
could not translate host name "db.unvqxcthzdtlvwxllrnq.supabase.co" to address
```

**Possible Causes:**
1. No internet connection / VPN issue
2. Firewall blocking PostgreSQL port (5432)
3. DNS resolution failure
4. Corporate network restrictions

---

## Next Steps (When Network is Resolved)

### 1. Test Database Connection
```bash
cd D:\Dash\backend
uv run python -c "from app.core.database import engine; print(engine.connect())"
```

### 2. Generate Initial Migration
```bash
uv run alembic revision --autogenerate -m "initial portfolio table"
```

### 3. Apply Migration to Database
```bash
uv run alembic upgrade head
```

### 4. Start the Development Server
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API
Open browser: `http://localhost:8000/docs`

---

## Test the CSV Upload Feature

### Sample Zerodha CSV Format
Create a file `test_portfolio.csv`:
```csv
instrument,qty.,avg. cost,ltp,cur. val,p&l,net chg.,day chg.
RELIANCE,10,2500.00,2600.00,26000,1000,+4%,+2%
TCS,5,3200.00,3300.00,16500,500,+3.1%,+1.5%
INFY,15,1400.00,1450.00,21750,750,+3.6%,+0.8%
```

### Test with cURL
```bash
curl -X POST "http://localhost:8000/api/v1/portfolio/upload-csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_portfolio.csv"
```

---

## What Each File Does

### Core Infrastructure
- **[app/core/config.py](backend/app/core/config.py)** - Loads environment variables securely
- **[app/core/database.py](backend/app/core/database.py)** - SQLAlchemy connection & session management

### Data Layer
- **[app/models/portfolio.py](backend/app/models/portfolio.py)** - Portfolio table definition
  - `user_id` - Links to Supabase Auth (UUID)
  - `ticker_symbol` - Stock ticker with exchange (e.g., RELIANCE.NS)
  - `quantity` - Shares owned (Numeric 18,4 precision)
  - `average_price` - Cost basis (Numeric 18,2 precision)

### Business Logic
- **[app/services/portfolio_parser.py](backend/app/services/portfolio_parser.py)** - CSV parsing engine
  - **BrokerDetector** - Auto-detects Zerodha vs Upstox format
  - **PortfolioCSVParser** - Extracts & validates holdings
  - **Ticker Normalization** - Adds `.NS` suffix for NSE stocks

### API Layer
- **[app/api/v1/portfolio.py](backend/app/api/v1/portfolio.py)** - FastAPI endpoints
  - `POST /api/v1/portfolio/upload-csv` - Bulk upload from CSV
  - `GET /api/v1/portfolio/` - Get user's portfolio
  - `POST /api/v1/portfolio/` - Manually add single holding

### Validation
- **[app/schemas/portfolio.py](backend/app/schemas/portfolio.py)** - Pydantic models
  - Enforces decimal precision (4 places for quantity, 2 for price)
  - Type safety for all API requests/responses

---

## Corporate Standards Implemented 

1. **Type Safety** - Every field validated with Pydantic
2. **Database Migrations** - Alembic tracks all schema changes
3. **Error Handling** - Detailed HTTP error codes & messages
4. **Separation of Concerns** - Models/Services/API layers isolated
5. **Environment Config** - Secrets in `.env`, never hardcoded
6. **Decimal Precision** - Financial data uses `Numeric`, never `Float`

---

## Architecture Decisions

### Why No ALE (Application-Level Encryption)?
After discussion, we chose **utility over paranoia**:
- The system needs to see `quantity` and `average_price` to calculate "Material Change" urgency
- "40% of your portfolio crashed" vs "0.5% of your portfolio crashed" requires magnitude context
- Instead, we will use **Row-Level Security (RLS)** in Supabase (User A can never see User B's data)

### Why Supabase/PostgreSQL over MongoDB?
- **State Comparison** - "Snapshot T1 - Snapshot T0" is SQL-native
- **ACID Compliance** - Financial data needs transactional consistency
- **Extensibility** - Supabase gives us Auth + Real-time triggers for free

### Why `.NS` suffix for tickers?
- Yahoo Finance requires exchange identifiers
- NSE (National Stock Exchange) → `.NS`
- BSE (Bombay Stock Exchange) → `.BO`

---

## Troubleshooting

### If migrations fail:
```bash
# Drop all tables and retry
uv run alembic downgrade base
uv run alembic upgrade head
```

### If dependencies are missing:
```bash
uv sync
```

### If .env is not found:
```bash
# Ensure .env is in backend/ folder (not root)
ls D:\Dash\backend\.env
```

---

## What's Next (Phase 2)

Once the network issue is resolved and the server is running, we move to:

1. **Background Workers** - Celery + Redis for snapshot jobs
2. **Yahoo Finance Fetcher** - Pull 90-day OHLC data
3. **Snapshot Engine** - Trend/Volatility/Fundamental analysis
4. **Change Detection** - Compare Snapshot_T1 vs Snapshot_T0
5. **LLM Integration** - "Why this matters" explanations

---

## Questions?

Review the code in each file. Every line has comments explaining the "why."
The philosophy: **"State → State → Difference"** is baked into the schema design.

When you're ready to continue, just say **"Network is fixed, let's test it"** and we'll validate the full system.
