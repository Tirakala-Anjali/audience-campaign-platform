"""
AudienceFlow — One-shot database setup script.

Run ONCE after PostgreSQL is installed and running:
    cd backend
    .venv\\Scripts\\activate
    python setup_db.py

What it does:
  1. Creates the 'audienceflow' database if it doesn't exist.
  2. Runs all Alembic migrations (creates all 11 tables).
  3. Seeds the default roles (Admin, Campaign Manager, Communication Team).
  4. Prints a confirmation summary.
"""
import os
import sys
import subprocess

# ── Resolve paths ────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
VENV   = os.path.join(BASE, ".venv", "Scripts", "python.exe")
PYTHON = VENV if os.path.exists(VENV) else sys.executable

# ── Step 1: create the database ───────────────────────────────────────────────
print("=" * 60)
print("  AudienceFlow — Database Setup")
print("=" * 60)
print()
print("Step 1: Creating 'audienceflow' database …")

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    # Connect to the default 'postgres' database first
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if database already exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'audienceflow'")
    if cur.fetchone():
        print("  ✓  Database 'audienceflow' already exists — skipping creation.")
    else:
        cur.execute("CREATE DATABASE audienceflow")
        print("  ✓  Database 'audienceflow' created.")

    cur.close()
    conn.close()

except psycopg2.OperationalError as e:
    print(f"  ✗  Cannot connect to PostgreSQL: {e}")
    print()
    print("  Make sure PostgreSQL is running and the password is 'postgres'.")
    print("  If you used a different password during install, update:")
    print("    backend/.env  →  DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/audienceflow")
    sys.exit(1)

# ── Step 2: run Alembic migrations ────────────────────────────────────────────
print()
print("Step 2: Running Alembic migrations …")
result = subprocess.run(
    [PYTHON, "-m", "alembic", "upgrade", "head"],
    cwd=BASE, capture_output=True, text=True
)
if result.returncode == 0:
    print("  ✓  All migrations applied successfully.")
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            print(f"     {line}")
else:
    print("  ✗  Migration failed:")
    print(result.stderr)
    sys.exit(1)

# ── Step 3: seed roles ────────────────────────────────────────────────────────
print()
print("Step 3: Seeding default roles …")
sys.path.insert(0, BASE)
try:
    from app.database import SessionLocal
    from app.routers.auth import seed_roles, DEFAULT_ROLES
    db = SessionLocal()
    seed_roles(db)
    db.close()
    print(f"  ✓  Roles seeded: {', '.join(r['name'] for r in DEFAULT_ROLES)}")
except Exception as e:
    print(f"  ✗  Role seeding failed: {e}")
    sys.exit(1)

# ── Step 4: verify ────────────────────────────────────────────────────────────
print()
print("Step 4: Verifying setup …")
try:
    from app.database import SessionLocal
    from app.models.role import Role
    from app.models.user import User
    db = SessionLocal()
    roles  = db.query(Role).all()
    users  = db.query(User).count()
    db.close()
    print(f"  ✓  Roles in DB  : {[r.name for r in roles]}")
    print(f"  ✓  Users in DB  : {users}")
except Exception as e:
    print(f"  ✗  Verification failed: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("  Database setup complete! ✓")
print()
print("  Start the backend:")
print("    cd backend")
print("    .venv\\Scripts\\activate")
print("    uvicorn app.main:app --reload --port 8000")
print()
print("  Then run all tests including DB tests:")
print("    python test_register.py")
print("=" * 60)
