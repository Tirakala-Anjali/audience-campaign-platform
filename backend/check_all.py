"""
Master pre-flight check for AudienceFlow backend.
Run from backend/ with venv active.
"""
import os
import sys
import py_compile
import urllib.request
import urllib.error
import json
import socket
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

passed = 0
failed = 0
SECTION = "=" * 65


def ok(msg):
    global passed
    passed += 1
    print(f"  ✓  {msg}")


def fail(msg):
    global failed
    failed += 1
    print(f"  ✗  {msg}")


def section(title):
    print(f"\n{SECTION}")
    print(f"  {title}")
    print(SECTION)


# ── 1. Python syntax ──────────────────────────────────────────────────────────
section("1. Python syntax check")
skip = {"__pycache__", ".venv"}
syntax_ok = []
syntax_bad = []
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in skip]
    for f in files:
        if f.endswith(".py"):
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, BASE)
            try:
                py_compile.compile(fp, doraise=True)
                syntax_ok.append(rel)
            except py_compile.PyCompileError as e:
                syntax_bad.append((rel, str(e)))

print(f"  Files checked: {len(syntax_ok) + len(syntax_bad)}")
for rel, err in syntax_bad:
    fail(f"SYNTAX ERROR in {rel}: {err}")
if not syntax_bad:
    ok(f"All {len(syntax_ok)} Python files pass syntax check")

# ── 2. Import check ───────────────────────────────────────────────────────────
section("2. Deep import check")
sys.path.insert(0, BASE)

import importlib
modules = [
    "app.core.config",
    "app.database",
    "app.models",
    "app.schemas.auth",
    "app.schemas",
    "app.routers.health",
    "app.routers.auth",
    "app.main",
]
for mod in modules:
    try:
        importlib.import_module(mod)
        ok(f"import {mod}")
    except Exception as e:
        fail(f"import {mod}: {e}")

# ── 3. API endpoint tests (server must be on 8000) ────────────────────────────
section("3. API endpoint tests  (server on port 8000)")

db_up = False
try:
    s = socket.create_connection(("localhost", 5432), timeout=2)
    s.close()
    db_up = True
except Exception:
    pass

print(f"  PostgreSQL 5432: {'RUNNING' if db_up else 'DOWN'}")

def api(label, path, method="GET", data=None, expect=200):
    url = "http://localhost:8000" + path
    try:
        body = json.dumps(data).encode() if data else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=5) as r:
            payload = json.loads(r.read())
            if r.status == expect:
                ok(f"[{r.status}] {label}")
                return payload
            else:
                fail(f"[{r.status}] {label}  (expected {expect})")
    except urllib.error.HTTPError as e:
        pl = {}
        try:
            pl = json.loads(e.read())
        except Exception:
            pass
        if e.code == expect:
            detail = pl.get("detail", "")
            if isinstance(detail, list):
                detail = " | ".join(d.get("msg", "") for d in detail[:2])
            ok(f"[{e.code}] {label}  — {str(detail)[:80]}")
            return pl
        else:
            fail(f"[{e.code}] {label}  (expected {expect}): {pl}")
    except Exception as ex:
        fail(f"{label}: {ex}")
    return None

# Always-available tests
api("GET /", "/")
health = api("GET /health", "/health")
if health:
    db_status = health.get("database", "?")
    ok(f"  database field = '{db_status}'") if db_status == "connected" else fail(f"  database = '{db_status}' (PostgreSQL not reachable)")

api("GET /auth/roles", "/auth/roles")

api("POST /auth/register — missing fields → 422", "/auth/register", "POST",
    {"email": "x"}, expect=422)
api("POST /auth/register — weak password → 422", "/auth/register", "POST",
    {"name": "U", "email": "u@t.com", "phone": "1234567",
     "organization_name": "O", "password": "weakpass", "role": "Campaign Manager"},
    expect=422)
api("POST /auth/register — invalid email → 422", "/auth/register", "POST",
    {"name": "U", "email": "bademail", "phone": "1234567",
     "organization_name": "O", "password": "StrongPass@1", "role": "Campaign Manager"},
    expect=422)
api("POST /auth/register — short phone → 422", "/auth/register", "POST",
    {"name": "U", "email": "a@t.com", "phone": "123",
     "organization_name": "O", "password": "StrongPass@1", "role": "Campaign Manager"},
    expect=422)
api("POST /auth/register — Admin blocked → 400", "/auth/register", "POST",
    {"name": "Test User", "email": "u@t.com", "phone": "9876543210",
     "organization_name": "Test Org", "password": "StrongPass@1", "role": "Admin"},
    expect=400)

if db_up:
    import time
    ts = str(int(time.time()))
    email1 = f"reg{ts}@test.com"
    email2 = f"comm{ts}@test.com"

    reg = api("POST /auth/register — Campaign Manager → 201",
              "/auth/register", "POST",
              {"name": "Test User", "email": email1, "phone": "9876543210",
               "organization_name": "Test Org", "password": "StrongPass@1",
               "role": "Campaign Manager"},
              expect=201)

    api("POST /auth/register — duplicate email → 409",
        "/auth/register", "POST",
        {"name": "Test 2", "email": email1, "phone": "9876543210",
         "organization_name": "Org", "password": "StrongPass@1",
         "role": "Campaign Manager"},
        expect=409)

    api("POST /auth/register — Communication Team → 201",
        "/auth/register", "POST",
        {"name": "Comm User", "email": email2, "phone": "+44 7911 123456",
         "organization_name": "Comms Ltd", "password": "Secure#Pass9",
         "role": "Communication Team"},
        expect=201)

    api("POST /auth/register — invalid role → 400",
        "/auth/register", "POST",
        {"name": "Test User", "email": f"r{ts}@t.com", "phone": "9876543210",
         "organization_name": "Test Org", "password": "StrongPass@1",
         "role": "SuperAdmin"},
        expect=400)

    api("POST /auth/register — uppercase email duplicate → 409",
        "/auth/register", "POST",
        {"name": "Upper", "email": email1.upper(), "phone": "9876543210",
         "organization_name": "Org", "password": "StrongPass@1",
         "role": "Campaign Manager"},
        expect=409)

    # Login tests
    api("POST /auth/login — valid credentials → 200",
        "/auth/login", "POST",
        {"email": email1, "password": "StrongPass@1"},
        expect=200)

    # Verify JWT token from login works on protected endpoint
    import urllib.request, urllib.error, json as _json
    try:
        _login_data = _json.dumps({"email": email1, "password": "StrongPass@1"}).encode()
        _req = urllib.request.Request("http://localhost:8000/auth/login",
                                      data=_login_data,
                                      headers={"Content-Type": "application/json"},
                                      method="POST")
        with urllib.request.urlopen(_req, timeout=5) as _r:
            _resp = _json.loads(_r.read())
            _token = _resp.get("access_token", "")
        if _token:
            _me_req = urllib.request.Request("http://localhost:8000/auth/me",
                                             headers={"Authorization": f"Bearer {_token}"},
                                             method="GET")
            with urllib.request.urlopen(_me_req, timeout=5) as _r2:
                _me = _json.loads(_r2.read())
                ok(f"GET /auth/me with JWT → id={_me.get('id')} role={_me.get('role')}")
        else:
            fail("GET /auth/me — no token in login response")
    except Exception as _ex:
        fail(f"GET /auth/me JWT test: {_ex}")

    api("POST /auth/login — wrong password → 401",
        "/auth/login", "POST",
        {"email": email1, "password": "WrongPassword@1"},
        expect=401)

    api("POST /auth/login — unknown email → 401",
        "/auth/login", "POST",
        {"email": "nobody@nowhere.com", "password": "StrongPass@1"},
        expect=401)

    # ── GET /auth/me — unauthenticated → 401 ──────────────────────────
    api("GET /auth/me — no token → 401", "/auth/me", expect=401)

    # ── Campaign CRUD tests (require auth) ────────────────────────────
    # Get a fresh token for campaign tests
    login_resp = api("POST /auth/login — get token for campaigns",
                     "/auth/login", "POST",
                     {"email": email1, "password": "StrongPass@1"},
                     expect=200)
    token = login_resp.get("access_token", "") if login_resp else ""

    if token:
        import urllib.request as _ur

        def auth_api(label, path, method="GET", data=None, expect=200):
            """Like api() but with Authorization header."""
            url = "http://localhost:8000" + path
            try:
                body = json.dumps(data).encode() if data else None
                hdrs = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
                req = _ur.Request(url, data=body, headers=hdrs, method=method)
                with _ur.urlopen(req, timeout=5) as r:
                    payload = json.loads(r.read()) if r.status != 204 else {}
                    if r.status == expect:
                        ok(f"[{r.status}] {label}")
                        return payload
                    else:
                        fail(f"[{r.status}] {label}  (expected {expect})")
            except urllib.error.HTTPError as e:
                pl = {}
                try: pl = json.loads(e.read())
                except: pass
                if e.code == expect:
                    ok(f"[{e.code}] {label}")
                    return pl
                else:
                    fail(f"[{e.code}] {label}  (expected {expect}): {pl.get('detail','')}")
            except Exception as ex:
                fail(f"{label}: {ex}")
            return None

        # Campaigns list (empty or existing)
        auth_api("GET /campaigns — list campaigns", "/campaigns", expect=200)

        # Create a campaign
        created = auth_api("POST /campaigns — create draft", "/campaigns", "POST",
                           {"name": f"Test Campaign {ts}", "description": "Auto-test",
                            "status": "draft"}, expect=201)
        camp_id = created.get("id") if created else None

        if camp_id:
            # Get by ID
            auth_api(f"GET /campaigns/{camp_id} — get by id", f"/campaigns/{camp_id}", expect=200)

            # Update
            auth_api(f"PUT /campaigns/{camp_id} — update to active",
                     f"/campaigns/{camp_id}", "PUT",
                     {"status": "active", "name": f"Updated Campaign {ts}"}, expect=200)

            # Delete
            auth_api(f"DELETE /campaigns/{camp_id} — delete", f"/campaigns/{camp_id}",
                     method="DELETE", expect=204)

            # Confirm deleted
            auth_api(f"GET /campaigns/{camp_id} — verify deleted → 404",
                     f"/campaigns/{camp_id}", expect=404)
        else:
            fail("Campaign CRUD: could not get ID from created campaign")

        # Unauthenticated access to campaigns → 401
        api("GET /campaigns — no token → 401", "/campaigns", expect=401)

        # ── Dashboard tests ────────────────────────────────────────────
        stats = auth_api("GET /dashboard/stats — authenticated → 200",
                         "/dashboard/stats", expect=200)
        if stats:
            # Verify response has required fields
            required_fields = [
                "total_campaigns", "active_campaigns", "draft_campaigns",
                "total_audience_members", "total_registered_users",
                "status_breakdown", "recent_campaigns",
            ]
            missing = [f for f in required_fields if f not in stats]
            if missing:
                fail(f"GET /dashboard/stats — missing fields: {missing}")
            else:
                ok(f"GET /dashboard/stats — all required fields present")

            # Verify campaign counts are consistent
            total = stats.get("total_campaigns", 0)
            status_sum = sum(
                stats.get(f"{s}_campaigns", 0)
                for s in ["active", "draft", "paused", "completed", "cancelled"]
            )
            if total == status_sum:
                ok(f"GET /dashboard/stats — campaign counts consistent (total={total})")
            else:
                fail(f"GET /dashboard/stats — count mismatch: total={total} vs status_sum={status_sum}")

            # Verify registered_users ≥ 1 (we registered test users)
            users = stats.get("total_registered_users", 0)
            if users >= 1:
                ok(f"GET /dashboard/stats — registered_users={users} (≥1 ✓)")
            else:
                fail(f"GET /dashboard/stats — registered_users={users} (expected ≥1)")

        # Unauthenticated access to dashboard → 401
        api("GET /dashboard/stats — no token → 401", "/dashboard/stats", expect=401)

        # ── Audience CRUD tests ────────────────────────────────────────
        aud_list = auth_api("GET /audience — list → 200", "/audience", expect=200)

        aud_create = auth_api("POST /audience — create member → 201", "/audience", "POST",
            {"name": f"AuditMember {ts}", "email": f"aud{ts}@test.com",
             "phone": "9876543210", "city": "Mumbai", "gender": "Female",
             "consent_status": True, "preferred_channel": "email"}, expect=201)
        aud_id = aud_create.get("id") if aud_create else None

        if aud_id:
            auth_api(f"GET /audience/{aud_id} → 200", f"/audience/{aud_id}", expect=200)
            auth_api(f"PUT /audience/{aud_id} → 200", f"/audience/{aud_id}", "PUT",
                     {"city": "Pune", "consent_status": True}, expect=200)
            auth_api(f"DELETE /audience/{aud_id} → 204", f"/audience/{aud_id}",
                     method="DELETE", expect=204)

        stats_aud = auth_api("GET /audience/stats → 200", "/audience/stats", expect=200)
        if stats_aud:
            ok(f"GET /audience/stats — total={stats_aud.get('total')}")

        api("GET /audience — no token → 401", "/audience", expect=401)

        # ── Segment CRUD + preview tests ───────────────────────────────
        seg_list = auth_api("GET /segments → 200", "/segments", expect=200)

        seg_create = auth_api("POST /segments — create → 201", "/segments", "POST",
            {"name": f"Audit Segment {ts}",
             "filter_criteria": {"operator": "AND",
                "rules": [{"field": "city", "op": "eq", "value": "Mumbai"},
                           {"field": "consent_status", "op": "eq", "value": True}]}},
            expect=201)
        seg_id = seg_create.get("id") if seg_create else None

        if seg_id:
            auth_api(f"GET /segments/{seg_id} → 200", f"/segments/{seg_id}", expect=200)
            auth_api(f"PUT /segments/{seg_id} → 200", f"/segments/{seg_id}", "PUT",
                     {"description": "Updated"}, expect=200)
            auth_api(f"GET /segments/{seg_id}/members → 200",
                     f"/segments/{seg_id}/members", expect=200)
            auth_api(f"DELETE /segments/{seg_id} → 204", f"/segments/{seg_id}",
                     method="DELETE", expect=204)

        preview = auth_api("POST /segments/preview → 200", "/segments/preview", "POST",
            {"filter_criteria": {"operator": "AND",
                "rules": [{"field": "consent_status", "op": "eq", "value": True}]}},
            expect=200)
        if preview:
            ok(f"POST /segments/preview — matching_count={preview.get('matching_count',0)}")

        api("GET /segments — no token → 401", "/segments", expect=401)

        # ── Templates CRUD tests ───────────────────────────────────────
        tmpl_list = auth_api("GET /templates → 200", "/templates", expect=200)

        tmpl_create = auth_api("POST /templates — create → 201", "/templates", "POST",
            {"name": f"Audit Template {ts}", "channel": "email", "language": "en",
             "category": "promotional", "subject": "Hello {{name}}",
             "content": "Dear {{name}}, welcome to AudienceFlow!",
             "placeholders": ["name"], "tags": ["welcome"]}, expect=201)
        tmpl_id = tmpl_create.get("id") if tmpl_create else None

        if tmpl_id:
            auth_api(f"GET /templates/{tmpl_id} → 200", f"/templates/{tmpl_id}", expect=200)
            auth_api(f"PUT /templates/{tmpl_id} → 200", f"/templates/{tmpl_id}", "PUT",
                     {"tags": ["welcome", "updated"]}, expect=200)
            auth_api(f"DELETE /templates/{tmpl_id} → 204", f"/templates/{tmpl_id}",
                     method="DELETE", expect=204)

        api("GET /templates — no token → 401", "/templates", expect=401)

    else:
        fail("Campaign tests skipped — could not obtain token")
else:
    print("  (DB tests skipped — PostgreSQL not running)")

# ── Summary ───────────────────────────────────────────────────────────────────
section("SUMMARY")
total = passed + failed
print(f"  Passed: {passed}   Failed: {failed}   Total: {total}")
if failed == 0:
    print("  ALL TESTS PASSED ✓")
else:
    print(f"  {failed} FAILURE(S) — see above")

sys.exit(0 if failed == 0 else 1)
