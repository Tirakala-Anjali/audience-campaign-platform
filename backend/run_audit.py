"""
Milestone 1 Audit Script
Collects evidence for every verifiable requirement.
Run from backend/ with venv active.
"""
import os, sys, socket, json, urllib.request, urllib.error, py_compile, importlib, time

BASE   = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
BACK   = os.path.join(BASE, 'backend')
FRONT  = os.path.join(BASE, 'frontend')
OUT    = []

def h(title): OUT.append(f"\n{'='*72}\n  {title}\n{'='*72}")
def p(msg):   OUT.append(f"  {msg}")
def ok(msg):  OUT.append(f"  [PASS]  {msg}")
def fail(msg):OUT.append(f"  [FAIL]  {msg}")
def part(msg):OUT.append(f"  [PART]  {msg}")
def bk(msg):  OUT.append(f"  [BLOCKED] {msg}")
def nv(msg):  OUT.append(f"  [NV]    {msg}")

# ─── helpers ─────────────────────────────────────────────────────────────────
def file_exists(rel):
    return os.path.isfile(os.path.join(BASE, rel.replace('/', os.sep)))

def grep(rel, *patterns):
    fp = os.path.join(BASE, rel.replace('/', os.sep))
    if not os.path.isfile(fp): return {}
    txt = open(fp, encoding='utf-8', errors='ignore').read()
    return {p: (p in txt) for p in patterns}

def grep_dir(directory, *patterns):
    """Search all .py files in a directory for patterns."""
    results = {p: False for p in patterns}
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.venv'}]
        for f in files:
            if f.endswith('.py'):
                txt = open(os.path.join(root,f), encoding='utf-8', errors='ignore').read()
                for p in patterns:
                    if p in txt:
                        results[p] = True
    return results

def db_running():
    try: s=socket.create_connection(('localhost',5432),timeout=2); s.close(); return True
    except: return False

def api_call(path, method='GET', data=None, headers=None):
    url = 'http://localhost:8000' + path
    hdrs = {'Content-Type': 'application/json'}
    if headers: hdrs.update(headers)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}
    except Exception as ex:
        return None, str(ex)

def server_up():
    st, _ = api_call('/')
    return st == 200

# ─── File inventory ───────────────────────────────────────────────────────────
skip = {'__pycache__', '.venv', 'node_modules', 'dist', '.git'}
all_files = []
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in skip]
    for f in files:
        if not f.endswith('.pyc'):
            all_files.append(os.path.join(root,f).replace(BASE+os.sep,''))
all_files.sort()

# ═══════════════════════════════════════════════════════════════════════════════
h("FILE INVENTORY")
backend_py = [f for f in all_files if f.startswith('backend') and f.endswith('.py')
              and '.venv' not in f]
frontend_js = [f for f in all_files if f.startswith('frontend') and
               (f.endswith('.jsx') or f.endswith('.js') or f.endswith('.ts') or f.endswith('.tsx'))]
p(f"Total tracked files : {len(all_files)}")
p(f"Backend .py files   : {len(backend_py)}")
p(f"Frontend .js/.jsx   : {len(frontend_js)}")
p("Backend routers:")
for f in all_files:
    if 'routers' in f and f.endswith('.py') and '.venv' not in f:
        p(f"  {f}")
p("Backend models:")
for f in all_files:
    if 'models' in f and f.endswith('.py') and '.venv' not in f:
        p(f"  {f}")
p("Frontend pages:")
for f in all_files:
    if 'pages' in f and ('.jsx' in f or '.tsx' in f):
        p(f"  {f}")
p("Migrations:")
for f in all_files:
    if 'versions' in f and f.endswith('.py'):
        p(f"  {f}")

# ═══════════════════════════════════════════════════════════════════════════════
h("TASK 1 — Project Setup, Database, Landing Page")

# Backend structure
for rel in ['backend/app/main.py','backend/app/database.py','backend/app/core/config.py',
            'backend/requirements.txt','backend/alembic.ini','backend/alembic/env.py']:
    (ok if file_exists(rel) else fail)(f"File exists: {rel}")

# Models
models_needed = ['user','role','audience_member','segment','campaign','template',
                 'message','delivery_log','feedback']
models_dir = os.path.join(BACK,'app','models')
found_models = [m for m in models_needed
                if os.path.isfile(os.path.join(models_dir, m+'.py'))]
missing_models = [m for m in models_needed if m not in found_models]
ok(f"Models found: {found_models}") if not missing_models else part(f"Models found: {found_models}  MISSING: {missing_models}")

# CORS
main_txt = grep('backend/app/main.py', 'CORSMiddleware', 'allow_origins', 'allow_methods')
ok("CORS configured in main.py") if all(main_txt.values()) else fail(f"CORS missing: {main_txt}")

# Health endpoint
if server_up():
    st, body = api_call('/health')
    ok(f"GET /health → {st}: {body}") if st==200 else fail(f"GET /health → {st}: {body}")
else:
    bk("GET /health — server not responding on port 8000")

# Alembic migrations
migrations = [f for f in all_files if 'versions' in f and f.endswith('.py') and 'alembic' in f]
ok(f"Alembic migrations found: {len(migrations)}: {[os.path.basename(m) for m in migrations]}") if migrations else fail("No Alembic migrations found")

# env / secrets
env_ex = file_exists('backend/.env.example')
env_real = file_exists('backend/.env')
ok(".env.example exists") if env_ex else fail(".env.example missing")
ok(".env exists (local only, gitignored)") if env_real else nv(".env not present (may be missing or gitignored)")
gi = grep('.gitignore', 'backend/.env', '.env')
ok(".env is gitignored") if any(gi.values()) else fail(".env NOT in .gitignore — security risk!")

# Frontend
for rel in ['frontend/src/App.jsx','frontend/index.html','frontend/vite.config.js',
            'frontend/src/styles/global.css','frontend/src/pages/LandingPage.jsx',
            'frontend/src/services/api.js']:
    (ok if file_exists(rel) else fail)(f"Frontend file: {rel}")

app_checks = grep('frontend/src/App.jsx', 'BrowserRouter', 'Routes', 'Route')
ok(f"React Router configured: {app_checks}") if all(app_checks.values()) else fail(f"React Router: {app_checks}")
axios_check = grep('frontend/src/services/api.js','axios','VITE_API_BASE_URL','checkHealth')
ok(f"Axios + health check configured: {axios_check}") if all(axios_check.values()) else part(f"API service: {axios_check}")

# README
readme_checks = grep('README.md','Prerequisites','uvicorn','npm run dev','alembic upgrade')
ok("README covers setup") if all(readme_checks.values()) else part(f"README gaps: {readme_checks}")

# Syntax check all backend
syn_ok=0; syn_fail=0
for root,dirs,files in os.walk(BACK):
    dirs[:] = [d for d in dirs if d not in {'__pycache__','.venv'}]
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root,f)
            try: py_compile.compile(fp,doraise=True); syn_ok+=1
            except py_compile.PyCompileError as e: fail(f"Syntax error: {fp}: {e}"); syn_fail+=1
ok(f"Python syntax: {syn_ok} files OK, {syn_fail} failures")

# ═══════════════════════════════════════════════════════════════════════════════
h("TASK 2 — User Registration")

# Schema / validation
reg_schema = grep('backend/app/schemas/auth.py',
    'RegisterRequest','EmailStr','password','phone','organization_name','role','field_validator')
ok(f"RegisterRequest schema: {reg_schema}") if all(reg_schema.values()) else part(f"Schema: {reg_schema}")

# Bcrypt — no passlib dependency
auth_r = grep('backend/app/routers/auth.py','bcrypt','_hash_password','_verify_password',
              'RESTRICTED_ROLES','seed_roles')
ok(f"Auth router (bcrypt, seeding, restricted roles): {auth_r}") if all(auth_r.values()) else part(f"Auth router: {auth_r}")

# Default roles
roles_check = grep('backend/app/routers/auth.py','Admin','Campaign Manager','Communication Team')
ok(f"Default roles defined: {roles_check}") if all(roles_check.values()) else fail(f"Roles: {roles_check}")

# API tests
if server_up():
    # Missing fields → 422
    st, _ = api_call('/auth/register','POST',{'email':'x'})
    ok(f"Register missing fields → {st}") if st==422 else fail(f"Register missing fields → {st} (expected 422)")

    # Weak password → 422
    st, _ = api_call('/auth/register','POST',{
        'name':'Test','email':'t@t.com','phone':'1234567',
        'organization_name':'Org','password':'weak','role':'Campaign Manager'})
    ok(f"Register weak password → {st}") if st==422 else fail(f"Register weak password → {st} (expected 422)")

    # Admin blocked
    st, body = api_call('/auth/register','POST',{
        'name':'Test User','email':'t@t.com','phone':'9876543210',
        'organization_name':'Org','password':'StrongPass@1','role':'Admin'})
    ok(f"Register Admin blocked → {st}: {body.get('detail','')}") if st==400 else fail(f"Admin blocked → {st}")

    # Valid registration
    ts = str(int(time.time()))
    reg_email = f"audit{ts}@test.com"
    st, body = api_call('/auth/register','POST',{
        'name':'Audit User','email':reg_email,'phone':'9876543210',
        'organization_name':'Test Corp','password':'StrongPass@1','role':'Campaign Manager'})
    if st==201:
        ok(f"Valid registration → 201: id={body.get('user',{}).get('id')}, role={body.get('user',{}).get('role')}")
    else:
        fail(f"Valid registration → {st}: {body}")

    # Duplicate email
    st, body = api_call('/auth/register','POST',{
        'name':'Dup','email':reg_email,'phone':'9876543210',
        'organization_name':'Org','password':'StrongPass@1','role':'Campaign Manager'})
    ok(f"Duplicate email → {st}: {body.get('detail','')}") if st==409 else fail(f"Duplicate email → {st}")
else:
    bk("Task 2 API tests — server not running")

# Frontend
reg_page = grep('frontend/src/pages/RegisterPage.jsx',
    'organization_name','phone','role','password','confirmPassword','registerUser','strength')
ok(f"RegisterPage fields: {reg_page}") if all(reg_page.values()) else part(f"RegisterPage: {reg_page}")

# ═══════════════════════════════════════════════════════════════════════════════
h("TASK 3 — Login, JWT, RBAC")

jwt_checks = grep('backend/app/routers/auth.py',
    '_create_access_token','_decode_token','get_current_user','ALGORITHM','ACCESS_EXPIRE',
    'jwt.encode','jwt.decode','HTTPBearer')
ok(f"JWT implementation: {jwt_checks}") if all(jwt_checks.values()) else part(f"JWT: {jwt_checks}")

if server_up():
    # Login valid
    ts2 = str(int(time.time())-1)
    login_email = f"audit{str(int(time.time()))}@test.com"
    # Register first
    api_call('/auth/register','POST',{'name':'JWT Test','email':login_email,'phone':'9876543210',
        'organization_name':'Org','password':'StrongPass@1','role':'Campaign Manager'})
    st, body = api_call('/auth/login','POST',{'email':login_email,'password':'StrongPass@1'})
    token = body.get('access_token','') if st==200 else ''
    if st==200 and token:
        ok(f"Login → 200, token returned (length={len(token)})")
    else:
        fail(f"Login → {st}: {body}")

    # GET /auth/me with token
    if token:
        st2, me_body = api_call('/auth/me','GET',headers={'Authorization':f'Bearer {token}'})
        ok(f"GET /auth/me with JWT → {st2}: id={me_body.get('id')} role={me_body.get('role')}") if st2==200 else fail(f"GET /auth/me → {st2}")

    # GET /auth/me no token → 401
    st3, _ = api_call('/auth/me')
    ok(f"GET /auth/me no token → {st3}") if st3==401 else fail(f"GET /auth/me no token → {st3} (expected 401)")

    # Wrong password → 401
    st4, _ = api_call('/auth/login','POST',{'email':login_email,'password':'Wrong@Pass1'})
    ok(f"Login wrong password → {st4}") if st4==401 else fail(f"Login wrong password → {st4}")

    # Protected route without token
    st5, _ = api_call('/campaigns')
    ok(f"Protected /campaigns no token → {st5}") if st5==401 else fail(f"/campaigns no token → {st5} (expected 401)")

    # Protected route with token
    st6, _ = api_call('/campaigns','GET',headers={'Authorization':f'Bearer {token}'})
    ok(f"Protected /campaigns with JWT → {st6}") if st6==200 else fail(f"/campaigns with JWT → {st6}")
else:
    bk("Task 3 API tests — server not running")

# Frontend login
login_checks = grep('frontend/src/pages/LoginPage.jsx',
    'loginUser','access_token','localStorage','navigate','apiError')
ok(f"LoginPage wired to API: {login_checks}") if all(login_checks.values()) else part(f"Login page: {login_checks}")

# ProtectedRoute
pr = grep('frontend/src/App.jsx','ProtectedRoute','Navigate','access_token')
ok(f"ProtectedRoute implemented: {pr}") if all(pr.values()) else fail(f"ProtectedRoute: {pr}")

# RBAC — role-based dashboard
rbac = grep('frontend/src/pages/DashboardPage.jsx','isCommTeam','user_role','Communication Team','Campaign Manager')
ok(f"Role-based dashboard views: {rbac}") if all(rbac.values()) else part(f"Dashboard RBAC: {rbac}")

# Backend RBAC check
p("NOTE: Backend role enforcement is currently at route-level (JWT required for all protected routes).")
p("      Fine-grained per-role API permissions (e.g. Admin-only endpoints) are NOT yet implemented.")

# ═══════════════════════════════════════════════════════════════════════════════
h("TASK 4 — Audience Management")

audience_model = file_exists('backend/app/models/audience_member.py')
ok("AudienceMember model exists") if audience_model else fail("AudienceMember model MISSING")

audience_router = file_exists('backend/app/routers/audience.py') or \
                  any('audience' in f for f in all_files if f.startswith('backend/app/routers'))
ok("Audience router exists") if audience_router else fail("Audience router MISSING — no /audience/* API endpoints")

audience_fields = grep('backend/app/models/audience_member.py',
    'name','email','phone','preferred_language','consent_status') if audience_model else {}
p(f"AudienceMember model fields present: {audience_fields}")
missing_fields = [f for f in ['name','email','phone','preferred_language','consent_status']
                  if not audience_fields.get(f,False)]
ok(f"Core audience fields OK") if not missing_fields else part(f"Missing fields in model: {missing_fields}")

# Check for missing fields per spec (age, gender, city, state, occupation etc.)
spec_fields = ['age','gender','city','state','occupation','department','preferred_channel']
if audience_model:
    spec_present = grep('backend/app/models/audience_member.py', *spec_fields)
    missing_spec = [k for k,v in spec_present.items() if not v]
    if missing_spec:
        fail(f"Spec fields MISSING from AudienceMember model: {missing_spec}")
    else:
        ok("All spec audience fields present in model")

if server_up():
    ts3 = str(int(time.time()))
    login_email3 = f"aud{ts3}@test.com"
    api_call('/auth/register','POST',{'name':'Aud Test','email':login_email3,'phone':'9876543210',
        'organization_name':'Org','password':'StrongPass@1','role':'Campaign Manager'})
    st_l, body_l = api_call('/auth/login','POST',{'email':login_email3,'password':'StrongPass@1'})
    aud_tok = body_l.get('access_token','') if st_l==200 else ''

    st, _ = api_call('/audience', headers={'Authorization':f'Bearer {aud_tok}'} if aud_tok else {})
    if st == 200: ok("GET /audience → 200")
    elif st == 401: fail("GET /audience → 401 (no token used, likely blocked)")
    elif st is None: fail("GET /audience → server error or route not found")
    else: fail(f"GET /audience → {st} (expected 200)")

    st2, _ = api_call('/audience/stats', headers={'Authorization':f'Bearer {aud_tok}'} if aud_tok else {})
    ok(f"GET /audience/stats → {st2}") if st2==200 else fail(f"GET /audience/stats → {st2} (MISSING)")
else:
    bk("Task 4 API tests — server not running")

# Frontend
audience_page = any('audience' in f.lower() or 'Audience' in f for f in all_files
                     if f.startswith('frontend/src/pages'))
ok("Audience management page exists") if audience_page else fail("Audience management page MISSING from frontend")

# ═══════════════════════════════════════════════════════════════════════════════
h("TASK 5 — Audience Segmentation")

seg_model = file_exists('backend/app/models/segment.py')
ok("Segment model exists") if seg_model else fail("Segment model MISSING")

seg_router = any('segment' in f for f in all_files
                 if f.startswith('backend/app/routers') and f.endswith('.py'))
ok("Segment router exists") if seg_router else fail("Segment router MISSING — no /segments/* endpoints")

if seg_model:
    seg_fields = grep('backend/app/models/segment.py',
        'name','description','filter_criteria')
    ok(f"Segment model fields: {seg_fields}") if all(seg_fields.values()) else part(f"Segment fields: {seg_fields}")

if server_up():
    ts4 = str(int(time.time()))
    login_email4 = f"seg{ts4}@test.com"
    api_call('/auth/register','POST',{'name':'Seg Test','email':login_email4,'phone':'9876543210',
        'organization_name':'Org','password':'StrongPass@1','role':'Campaign Manager'})
    st_l4, body_l4 = api_call('/auth/login','POST',{'email':login_email4,'password':'StrongPass@1'})
    seg_tok = body_l4.get('access_token','') if st_l4==200 else ''
    h4 = {'Authorization':f'Bearer {seg_tok}'} if seg_tok else {}

    for ep,method,data,exp in [
        ('/segments','GET',None,200),
        ('/segments/preview','POST',{'name':'Test','filter_criteria':{}},200),
    ]:
        st5, body5 = api_call(ep, method, data, headers=h4)
        ok(f"{method} {ep} → {st5}") if st5==exp else fail(f"{method} {ep} → {st5} (expected {exp})")
else:
    bk("Task 5 API tests — server not running")

seg_page = any('segment' in f.lower() or 'Segment' in f for f in all_files
               if f.startswith('frontend/src/pages'))
ok("Segmentation page exists") if seg_page else fail("Segmentation page MISSING from frontend")

# ═══════════════════════════════════════════════════════════════════════════════
h("TASK 6 — Campaigns and Templates")

camp_model = file_exists('backend/app/models/campaign.py')
tmpl_model = file_exists('backend/app/models/template.py')
ok("Campaign model exists") if camp_model else fail("Campaign model MISSING")
ok("Template model exists") if tmpl_model else fail("Template model MISSING")

if camp_model:
    camp_fields = grep('backend/app/models/campaign.py','name','description','status','start_at','end_at')
    ok(f"Campaign model fields: {camp_fields}") if all(camp_fields.values()) else part(f"Campaign fields: {camp_fields}")

# Check spec fields: type, objective, target_segments, channels, priority, creator
spec_camp_fields = ['priority','channels','objective']
if camp_model:
    spec_camp = grep('backend/app/models/campaign.py', *spec_camp_fields)
    missing_camp = [k for k,v in spec_camp.items() if not v]
    if missing_camp:
        fail(f"Spec campaign fields MISSING from model: {missing_camp}")
    else:
        ok("All spec campaign fields in model")

# Template model fields
if tmpl_model:
    tmpl_fields = grep('backend/app/models/template.py','name','content','channel','language')
    ok(f"Template model fields: {tmpl_fields}") if all(tmpl_fields.values()) else part(f"Template fields: {tmpl_fields}")

if server_up():
    ts5 = str(int(time.time()))
    login_email5 = f"camp{ts5}@test.com"
    api_call('/auth/register','POST',{'name':'Camp Test','email':login_email5,'phone':'9876543210',
        'organization_name':'Org','password':'StrongPass@1','role':'Campaign Manager'})
    st_l5, body_l5 = api_call('/auth/login','POST',{'email':login_email5,'password':'StrongPass@1'})
    camp_tok = body_l5.get('access_token','') if st_l5==200 else ''
    h5 = {'Authorization':f'Bearer {camp_tok}'} if camp_tok else {}

    # Campaign CRUD
    st_c, b_c = api_call('/campaigns','POST',{'name':f'Audit Camp {ts5}','status':'draft'},headers=h5)
    ok(f"POST /campaigns → {st_c}: id={b_c.get('id')}") if st_c==201 else fail(f"POST /campaigns → {st_c}: {b_c}")
    cid = b_c.get('id') if st_c==201 else None

    st_l6, _ = api_call('/campaigns',headers=h5)
    ok(f"GET /campaigns → {st_l6}") if st_l6==200 else fail(f"GET /campaigns → {st_l6}")

    if cid:
        st_u, _ = api_call(f'/campaigns/{cid}','PUT',{'status':'active','name':f'Updated {ts5}'},headers=h5)
        ok(f"PUT /campaigns/{cid} → {st_u}") if st_u==200 else fail(f"PUT /campaigns/{cid} → {st_u}")
        st_d, _ = api_call(f'/campaigns/{cid}','DELETE',headers=h5)
        ok(f"DELETE /campaigns/{cid} → {st_d}") if st_d==204 else fail(f"DELETE /campaigns/{cid} → {st_d}")

    # Templates
    st_t, _ = api_call('/templates',headers=h5)
    ok(f"GET /templates → {st_t}") if st_t==200 else fail(f"GET /templates → {st_t} (route may be missing)")
    st_tc, b_tc = api_call('/templates','POST',
        {'name':f'Tmpl {ts5}','channel':'email','language':'en','content':'Hello {{name}}'},headers=h5)
    ok(f"POST /templates → {st_tc}: id={b_tc.get('id')}") if st_tc==201 else fail(f"POST /templates → {st_tc}: {b_tc}")
else:
    bk("Task 6 API tests — server not running")

# Frontend campaign page
camp_page = any('Campaign' in f or 'campaign' in f for f in all_files
                if f.startswith('frontend/src/pages') and ('.jsx' in f or '.tsx' in f))
ok("Campaigns page exists") if camp_page else fail("Campaigns page MISSING")

tmpl_page = any('Template' in f or 'template' in f for f in all_files
                if f.startswith('frontend/src/pages') and ('.jsx' in f or '.tsx' in f))
ok("Templates page exists") if tmpl_page else fail("Templates page MISSING from frontend")

# ═══════════════════════════════════════════════════════════════════════════════
h("ENVIRONMENT / INFRASTRUCTURE")
p(f"PostgreSQL port 5432: {'RUNNING' if db_running() else 'NOT RUNNING'}")
p(f"Backend port 8000:   {'RESPONDING' if server_up() else 'NOT RESPONDING'}")
dist_exists = os.path.isdir(os.path.join(FRONT,'dist'))
p(f"Frontend dist/ built: {'YES' if dist_exists else 'NO'}")

# ── Write output ──────────────────────────────────────────────────────────────
report = '\n'.join(OUT)
print(report)

# Save raw findings
findings_path = os.path.join(BASE, 'audit_findings.txt')
with open(findings_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"\n\nFindings saved to: {findings_path}")
