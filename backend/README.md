# AudienceFlow — Backend API

FastAPI + SQLAlchemy + PostgreSQL backend for the AudienceFlow platform.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.110 |
| Server | Uvicorn |
| ORM | SQLAlchemy 2 |
| Database | PostgreSQL 15+ |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Settings | pydantic-settings |

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory, CORS, routers
│   ├── database.py          # Engine, SessionLocal, Base, get_db()
│   ├── core/
│   │   └── config.py        # Settings loaded from .env
│   ├── models/              # SQLAlchemy ORM models (9 tables + 2 junction)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/
│   │   └── health.py        # GET /health
│   └── services/            # Business logic (future milestones)
├── alembic/
│   ├── env.py               # Alembic runtime config
│   ├── script.py.mako       # Migration file template
│   └── versions/
│       └── 001_initial_schema.py
├── alembic.ini
├── requirements.txt
└── .env.example
```

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip

## Setup

### 1. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your real PostgreSQL credentials
```

### 4. Create the PostgreSQL database

```sql
-- Run in psql or pgAdmin
CREATE DATABASE audienceflow;
CREATE USER audienceflow_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE audienceflow TO audienceflow_user;
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the development server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API root:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API root info |
| GET | `/health` | Health + DB connectivity check |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc documentation |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECRET_KEY` | Yes | JWT signing key (future auth) |
| `CORS_ORIGINS` | No | Allowed frontend origins |
| `OPENAI_API_KEY` | No | Future AI integration |
| `SENDGRID_API_KEY` | No | Future email delivery |
| `TWILIO_API_KEY` | No | Future SMS delivery |

## Alembic Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# Roll back all migrations
alembic downgrade base

# Check current revision
alembic current

# Show migration history
alembic history --verbose

# Generate a new auto-migration (requires live DB)
alembic revision --autogenerate -m "describe your change"
```

## Troubleshooting

**`psycopg2` import error**
```
pip install psycopg2-binary
```

**`ModuleNotFoundError: No module named 'app'`**
Run uvicorn from the `backend/` directory, not from `backend/app/`.

**Alembic `FAILED: Can't locate revision identified by '...'`**
The migration file exists but PostgreSQL hasn't been updated. Run `alembic upgrade head`.

**`connection refused` on port 5432**
Ensure PostgreSQL is running: `pg_ctl start` or start the PostgreSQL service.
