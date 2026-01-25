# Dash Backend - AI Stock Intelligence Platform

Backend service for material change detection and stock intelligence.

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (via Supabase)
- `uv` package manager

### Installation

```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your Supabase credentials

# Initialize database migrations
uv run alembic upgrade head
```

### Running the Server

```bash
# Development mode with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Configuration and database
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── alembic/          # Database migrations
└── tests/            # Test suite
```

## Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## API Endpoints

### Portfolio Management
- `POST /api/v1/portfolio/upload-csv` - Upload Zerodha/Upstox CSV
- `GET /api/v1/portfolio/` - Get user portfolio
- `POST /api/v1/portfolio/` - Add single holding

## Corporate Standards
- **Type Safety**: All data validated with Pydantic
- **Database**: Alembic migrations for version control
- **Error Handling**: Detailed error messages with proper HTTP codes
- **Testing**: Pytest suite (coming soon)
