# AI Stock Intelligence Platform - Backend

A calm, trustworthy stock intelligence backend that tells users **what changed**, **why it matters**, and **when to worry**.

## Philosophy

- Start with **change detection**, not prediction
- Heavy intelligence runs **offline/in background**  
- Users only see **clear conclusions**, never raw process
- LLMs for **reasoning and explanation**, not math or prediction
- Portfolio is the anchor, not dashboards

## Tech Stack

- **Python 3.14+**
- **FastAPI** - Web framework
- **PostgreSQL** - Main database (users, portfolios, snapshots)
- **SQLAlchemy** - Async ORM
- **yfinance** - Market data
- **Pydantic** - Data validation
- **uv** - Package management

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   │   ├── auth.py      # Authentication
│   │   ├── portfolio.py # Portfolio management
│   │   ├── stocks.py    # Stock info & analysis
│   │   ├── insights.py  # Change insights
│   │   └── snapshots.py # Snapshot management
│   ├── data/          # Data providers
│   │   └── yahoo.py     # Yahoo Finance provider
│   ├── db/            # Database
│   │   ├── base.py      # DB configuration
│   │   └── models.py    # SQLAlchemy models
│   ├── jobs/          # Background jobs
│   │   ├── snapshot_job.py
│   │   └── change_detection_job.py
│   ├── config.py      # Settings
│   └── main.py        # FastAPI app
├── core/
│   ├── snapshots/     # Snapshot logic
│   │   ├── builder.py   # Build snapshots
│   │   ├── comparator.py # Compare snapshots
│   │   └── models.py    # Snapshot models
│   └── analysis/      # Analysis modules
│       ├── trend.py     # Trend analysis
│       ├── risk.py      # Risk analysis
│       └── fundamentals.py
├── llm/               # LLM integration
│   ├── prompts.py     # Prompt templates
│   └── chains.py      # LLM chains
└── test/              # Tests
```

## Core Feature: Material Change Detection

The core capability is answering:
> "Did anything meaningful change for this stock since last time?"

### How It Works

1. **Snapshots**: Store point-in-time state for each stock
   - Trend state (up/down/sideways)
   - Volatility bucket (low/normal/high)
   - Upcoming events (earnings window)
   - Fundamental health

2. **Comparison**: `Change = Snapshot_T1 - Snapshot_T0`
   - Detect trend reversals
   - Detect volatility spikes
   - Detect fundamental shifts
   - No ML needed - deterministic rules

3. **Insights**: LLMs explain what changes mean
   - What changed
   - Why it matters
   - What to watch (invalidation)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Get JWT token
- `GET /api/v1/auth/me` - Get current user

### Portfolio
- `GET /api/v1/portfolio/` - List portfolios
- `POST /api/v1/portfolio/` - Create portfolio
- `GET /api/v1/portfolio/{id}` - Get portfolio
- `POST /api/v1/portfolio/{id}/stocks` - Add stock
- `GET /api/v1/portfolio/{id}/summary` - Get summary with changes

### Stocks
- `GET /api/v1/stocks/search` - Search stocks
- `GET /api/v1/stocks/{symbol}/price` - Current price
- `GET /api/v1/stocks/{symbol}/status` - Quick status
- `GET /api/v1/stocks/{symbol}/analysis` - Full analysis

### Insights
- `GET /api/v1/insights/portfolio/{id}` - Portfolio insights
- `GET /api/v1/insights/portfolio/{id}/weekly` - Weekly report
- `GET /api/v1/insights/stock/{symbol}` - Stock insights

### Snapshots
- `GET /api/v1/snapshots/stock/{symbol}/latest` - Latest snapshot
- `GET /api/v1/snapshots/stock/{symbol}/compare` - Compare snapshots
- `POST /api/v1/snapshots/stock/{symbol}/create` - Create snapshot

## Getting Started

### Prerequisites

- Python 3.14+
- PostgreSQL
- uv (package manager)

### Installation

```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL, etc.

# Run the server
uv run uvicorn app.main:app --reload
```

### Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://localhost:5432/dash
SECRET_KEY=your-secret-key
DEBUG=true
```

## Running Tests

```bash
uv run pytest test/ -v
```

## Development

API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Status

This is MVP scaffolding. Key areas to implement:
- [ ] Full database integration in routes
- [ ] Authentication with proper JWT
- [ ] Background job scheduling
- [ ] LLM integration for insights
- [ ] WebSocket for real-time updates
