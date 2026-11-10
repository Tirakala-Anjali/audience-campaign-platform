"""
AudienceFlow — Registration Feature Test Suite
Run: python test_register.py   (server on port 8000 must be running)

Tests are split into:
  Group A — work WITHOUT PostgreSQL (validation + logic checks)
  Group B — require a live PostgreSQL database (DB-persisted checks)
"""
import json
import socket
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8000"
passed = 0
failed = 0
skipped = 0


# ─── Helpers ──────────────────────────────────────────────────

def db_running():
    try:
        s = socket.create_connection(("localhost", 5432), timeout=2)
        s.close()
        return True
    except Exception:
        return False


def call(label, path, method="GET", data=None, expect=200):
    global passed, failed
    url = BASE + path
    try:
        body = json.dumps(data).encode() if data else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req) as r:
            payload = json.loads(r.read())
            if r.status == expect:
                passed += 1
                extra = ""
                if "user" in payload:
                    u = payload["user"]
                    extra = f"  →  id={u['id']} role={u['role']}"
                print(f"  ✓  [{r.status}] {label}{extra}")
            else:
                failed += 1
                print(f"  ✗  [{r.status}] {label}  — expected {expect}")
    except urllib.error.HTTPError as e:
        payload = {}
        try:
            payload = json.loads(e.read())
        except Exception:
            pass
        if e.code == expect:
            passed += 1
            detail = payload.get("detail", "")
            if isinstance(detail, list):
                detail = " | ".join(d.get("msg", "") for d in detail[:2])
            print(f"  ✓  [{e.code}] {label}  — {str(detail)[:100]}")
        else:
            failed += 1
            print(f"  ✗  [{e.code}] {label}  — expected {expect}: {payload}")
    except Exception as ex:
        failed += 1
        print(f"  ✗  {label}: {ex}")


# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("  AudienceFlow — Registration API Test Suite")
print("=" * 65)

DB_UP = db_running()
print(f"  PostgreSQL on :5432  → {'RUNNING ✓' if DB_UP else 'NOT RUNNING (Group B will be skipped)'}")
print()

# ───────────────────────────────────────────────────────────────
print("── Group A  (no database needed) ─────────────────────────────")

# Infrastructure
call("GET /", "/")
call("GET /health", "/health")

# GET /auth/roles — when DB is down returns fallback list (200), when up returns DB roles
if DB_UP:
    call("GET /auth/roles  — returns DB roles", "/auth/roles", expect=200)
else:
    call("GET /auth/roles  — fallback list when DB down", "/auth/roles", expect=200)

# Pydantic validation — never reaches DB
call(
    "POST /auth/register  — missing all fields → 422",
    "/auth/register", "POST",
    data={"email": "x"},
    expect=422,
)
call(
    "POST /auth/register  — weak password → 422",
    "/auth/register", "POST",
    data={
        "name": "User", "email": "user@test.com",
        "phone": "9876543210", "organization_name": "Org",
        "password": "weakpass",          # no uppercase/digit/special
        "role": "Campaign Manager",
    },
    expect=422,
)
call(
    "POST /auth/register  — invalid email format → 422",
    "/auth/register", "POST",
    data={
        "name": "User", "email": "not-an-email",
        "phone": "9876543210", "organization_name": "Org",
        "password": "StrongPass@1", "role": "Campaign Manager",
    },
    expect=422,
)
call(
    "POST /auth/register  — short phone → 422",
    "/auth/register", "POST",
    data={
        "name": "User", "email": "short@test.com",
        "phone": "123",               # < 7 chars
        "organization_name": "Org",
        "password": "StrongPass@1", "role": "Campaign Manager",
    },
    expect=422,
)

# Admin blocked — checked before any DB call
call(
    "POST /auth/register  — Admin role blocked → 400",
    "/auth/register", "POST",
    data={
        "name": "Hacker", "email": "h@test.com",
        "phone": "9876543210", "organization_name": "Evil Corp",
        "password": "StrongPass@1", "role": "Admin",
    },
    expect=400,
)

# ───────────────────────────────────────────────────────────────
print()
print("── Group B  (requires live PostgreSQL) ───────────────────────")

if not DB_UP:
    skipped += 5
    print("  ⚠  SKIPPED — PostgreSQL is not running.")
    print()
    print("  To enable Group B tests:")
    print("  1. Install PostgreSQL 15+  →  https://www.postgresql.org/download/windows/")
    print("  2. Run in psql:")
    print("       CREATE DATABASE audienceflow;")
    print("  3. Set DATABASE_URL in backend/.env, then:")
    print("       cd backend")
    print("       .venv\\Scripts\\activate")
    print("       alembic upgrade head")
    print("       python test_register.py")
else:
    call(
        "POST /auth/register  — Campaign Manager → 201",
        "/auth/register", "POST",
        data={
            "name": "Test User",
            "email": "testuser@audienceflow.com",
            "phone": "9876543210",
            "organization_name": "Test Organisation",
            "password": "StrongPass@1",
            "role": "Campaign Manager",
        },
        expect=201,
    )
    call(
        "POST /auth/register  — duplicate email → 409",
        "/auth/register", "POST",
        data={
            "name": "Test User 2",
            "email": "testuser@audienceflow.com",      # duplicate
            "phone": "9876543210",
            "organization_name": "Another Org",
            "password": "StrongPass@1",
            "role": "Campaign Manager",
        },
        expect=409,
    )
    call(
        "POST /auth/register  — Communication Team → 201",
        "/auth/register", "POST",
        data={
            "name": "Comm User",
            "email": "comm@audienceflow.com",
            "phone": "+44 7911 123456",
            "organization_name": "Comms Ltd",
            "password": "Secure#Pass9",
            "role": "Communication Team",
        },
        expect=201,
    )
    call(
        "POST /auth/register  — invalid role → 400",
        "/auth/register", "POST",
        data={
            "name": "User", "email": "role@audienceflow.com",
            "phone": "9876543210", "organization_name": "Org",
            "password": "StrongPass@1", "role": "SuperAdmin",
        },
        expect=400,
    )
    call(
        "POST /auth/register  — email case-insensitive duplicate → 409",
        "/auth/register", "POST",
        data={
            "name": "Test Upper",
            "email": "TestUser@audienceflow.com",     # same as first, different case
            "phone": "9876543210",
            "organization_name": "Org",
            "password": "StrongPass@1",
            "role": "Campaign Manager",
        },
        expect=409,
    )

# ═══════════════════════════════════════════════════════════════
print()
print("=" * 65)
total = passed + failed
print(f"  Passed: {passed}   Failed: {failed}   Skipped: {skipped}")
if failed == 0:
    print("  ALL AVAILABLE TESTS PASSED ✓")
else:
    print(f"  {failed} TEST(S) FAILED")
print("=" * 65)
sys.exit(0 if failed == 0 else 1)
