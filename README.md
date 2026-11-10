# AudienceFlow — Audience Management & Campaign Planning Platform

> "Understand Your Audience. Create Smarter Campaigns. Build Stronger Connections."

A full-stack SaaS web application for managing audience members, creating campaigns,
planning multi-channel outreach, and tracking delivery performance — built as an
Infosys internship project.

---

## Features Implemented

| Milestone | Feature | Status |
|-----------|---------|--------|
| 1 | React landing page (Hero, Features, Workflow, CTA, Footer) | ✅ |
| 1 | User registration with validation, bcrypt hashing, role selection | ✅ |
| 1 | User login with JWT token generation | ✅ |
| 1 | `GET /auth/me` — protected profile endpoint | ✅ |
| 1 | `GET /auth/roles` — dynamic role list | ✅ |
| 1 | `GET /health` — app + database status | ✅ |
| 1 | PostgreSQL schema — 11 tables via Alembic (migration head: 002) | ✅ |
| 1 | Role seeding — Admin, Campaign Manager, Communication Team | ✅ |
| 1 | Admin self-assignment blocked on public registration | ✅ |
| 2 | Dashboard page with live statistics from database | ✅ |
| 2 | Campaign Management — create, view, edit, delete | ✅ |
| 2 | JWT-protected campaign and dashboard API routes | ✅ |
| 2 | Navbar updates dynamically based on login state | ✅ |
| 2 | Frontend production build — 1541 modules, 0 errors | ✅ |
| 2 | Backend test suite — **41/41 tests passing** | ✅ |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite 5 |
| Routing | React Router DOM v6 |
| HTTP client | Axios |
| Icons | Lucide React |
| Backend | FastAPI 0.143+ |
| Server | Uvicorn |
| ORM | SQLAlchemy 2.1+ |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Validation | Pydantic v2 + pydantic-settings |
| Password hashing | bcrypt 5 (Python 3.14 compatible) |

---

## Project Structure

```
audience-campaign-platform/
├── frontend/                        # React + Vite
│   ├── src/
│   │   ├── components/              # Navbar, Footer, FeatureCard, StepCard
│   │   ├── layouts/MainLayout.jsx
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx        # POST /auth/login → JWT stored
│   │   │   ├── RegisterPage.jsx     # POST /auth/register
│   │   │   ├── DashboardPage.jsx    # GET /dashboard/stats (protected)
│   │   │   └── CampaignsPage.jsx    # Full CRUD (protected)
│   │   ├── services/api.js          # Axios client + all API functions
│   │   └── styles/
│   ├── .env.example
│   └── package.json
│
├── backend/                         # FastAPI
│   ├── app/
│   │   ├── core/config.py           # pydantic-settings (reads .env)
│   │   ├── database.py              # SQLAlchemy engine + get_db()
│   │   ├── main.py                  # App factory, CORS, routers
│   │   ├── models/                  # 9 ORM models + 2 junction tables
│   │   ├── routers/
│   │   │   ├── auth.py              # /auth/register, /login, /me, /roles
│   │   │   ├── campaigns.py         # /campaigns CRUD
│   │   │   ├── dashboard.py         # /dashboard/stats
│   │   │   └── health.py            # /health
│   │   └── schemas/                 # Pydantic request/response models
│   ├── alembic/versions/            # DB migrations 001, 002
│   ├── check_all.py                 # Full test suite (41 tests)
│   ├── .env.example
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

## Database ER Diagram

```mermaid
erDiagram
    roles { int id PK; string name; string description }
    users { int id PK; string name; string email; string phone; string organization_name; string password_hash; int role_id FK }
    audience_members { int id PK; string name; string email; string phone; boolean consent_status }
    segments { int id PK; string name; json filter_criteria }
    campaigns { int id PK; string name; string description; string status; datetime start_at; datetime end_at }
    templates { int id PK; string name; string channel; text content }
    messages { int id PK; int campaign_id FK; int audience_member_id FK; int template_id FK; string status }
    delivery_logs { int id PK; int message_id FK; string delivery_status }
    feedback { int id PK; int audience_member_id FK; int campaign_id FK; int rating }
    segment_members { int segment_id FK; int audience_member_id FK }
    campaign_segments { int campaign_id FK; int segment_id FK }

    roles ||--o{ users : "assigned to"
    campaigns ||--o{ messages : "contains"
    audience_members ||--o{ messages : "receives"
    messages ||--o{ delivery_logs : "logged in"
    campaigns ||--o{ feedback : "receives"
```

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ (3.14 tested) |
| Node.js | 18+ (v24 tested) |
| PostgreSQL | 15+ (16 tested) |
| npm | 9+ |

---

## Installation

### Backend

```powershell
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY
```

### Frontend

```powershell
cd frontend
npm install
```

---

## Environment Variables

### `backend/.env`

```env
# IMPORTANT: Use postgresql+psycopg2:// prefix
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/audienceflow

# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-min-32-chars
```

> **Never commit the real `.env` file.** It is in `.gitignore`.

### `frontend/.env` (optional)

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Database Setup

```sql
-- Run in psql or pgAdmin
CREATE DATABASE audienceflow;
```

Then run migrations:

```powershell
cd backend
.venv\Scripts\activate
alembic upgrade head
```

Or use the one-shot setup script:

```powershell
python setup_db.py
```

---

## Starting the Application

### Terminal 1 — Backend

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Landing page |
| http://localhost:5173/register | Register account |
| http://localhost:5173/login | Login |
| http://localhost:5173/dashboard | Dashboard (login required) |
| http://localhost:5173/campaigns | Campaign management (login required) |
| http://localhost:8000/docs | Swagger UI — all API endpoints |
| http://localhost:8000/health | Health check |

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | API root |
| GET | `/health` | No | App + DB status |
| GET | `/auth/roles` | No | Roles for registration |
| POST | `/auth/register` | No | Register new account |
| POST | `/auth/login` | No | Login → JWT token |
| GET | `/auth/me` | JWT | Current user profile |
| GET | `/campaigns` | JWT | List campaigns |
| POST | `/campaigns` | JWT | Create campaign |
| GET | `/campaigns/{id}` | JWT | Get campaign |
| PUT | `/campaigns/{id}` | JWT | Update campaign |
| DELETE | `/campaigns/{id}` | JWT | Delete campaign |
| GET | `/dashboard/stats` | JWT | Dashboard statistics |

### Password Policy

Passwords must have 8+ chars, uppercase, lowercase, number, and special character.
Stored as bcrypt hashes — never in plain text.

---

## Running Tests

```powershell
cd backend
.venv\Scripts\activate
python check_all.py
```

**Expected: 41/41 tests passed**

Tests cover:
- Python syntax (40 files)
- Deep module imports (8 modules)
- Registration: missing fields, weak password, invalid email, Admin blocked, valid roles, duplicates
- Login: valid credentials, wrong password, unknown email
- JWT: `/auth/me` with valid token, unauthenticated access rejected
- Campaigns: full CRUD with auth, unauthenticated rejected
- Dashboard: stats with auth, field validation, unauthenticated rejected

---

## Security

| Concern | Implementation |
|---------|---------------|
| Passwords | bcrypt `$2b$12$` hashes — never stored as plain text |
| JWT tokens | HS256, 8-hour expiry, `SECRET_KEY` from env |
| Admin assignment | Blocked during public registration |
| Login errors | Vague message — doesn't reveal which field failed |
| CORS | Restricted to `localhost:5173` |
| Secrets | All in `.env` (gitignored), never hardcoded |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `connection refused` port 5432 | Start PostgreSQL service |
| `DATABASE_URL` must use `postgresql+psycopg2://` | Required for SQLAlchemy 2.1+ |
| `ModuleNotFoundError: No module named 'app'` | Run uvicorn from `backend/` directory |
| CORS error in browser | Check `CORS_ORIGINS` in `.env` includes `http://localhost:5173` |
| Node not found | Restart terminal after installing Node.js |

---

## Git Setup (before submission)

```powershell
# From audience-campaign-platform/ root
git init
git add .
git commit -m "feat: AudienceFlow — Audience Management & Campaign Planning Platform"

# Push to GitHub
git remote add origin https://github.com/<your-username>/audienceflow.git
git branch -M main
git push -u origin main
```

> Verify `git status` shows no `.env` files before pushing.

---

*AudienceFlow — Infosys Internship Project | Full-Stack Audience Campaign Platform*
