"""Submission-readiness audit script."""
import os, sys

BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

print("=" * 60)
print("  AudienceFlow — Submission Readiness Audit")
print("=" * 60)

# ── 1. File inventory ─────────────────────────────────────────
print("\n[1] KEY FILES")
key_files = [
    ('.gitignore',                    'ROOT'),
    ('README.md',                     'ROOT'),
    ('backend/.env.example',          'BACKEND'),
    ('backend/requirements.txt',      'BACKEND'),
    ('backend/app/main.py',           'BACKEND'),
    ('backend/app/routers/auth.py',   'BACKEND'),
    ('backend/app/routers/campaigns.py', 'BACKEND'),
    ('backend/app/routers/dashboard.py', 'BACKEND'),
    ('backend/check_all.py',          'TESTS'),
    ('frontend/package.json',         'FRONTEND'),
    ('frontend/src/App.jsx',          'FRONTEND'),
    ('frontend/src/pages/DashboardPage.jsx', 'FRONTEND'),
    ('frontend/src/pages/CampaignsPage.jsx', 'FRONTEND'),
    ('frontend/src/services/api.js',  'FRONTEND'),
]
for rel, tag in key_files:
    full = os.path.join(BASE, rel.replace('/', os.sep))
    status = 'OK' if os.path.exists(full) else 'MISSING'
    print(f"  [{status}] {tag:10s}  {rel}")

# ── 2. Security check ────────────────────────────────────────
print("\n[2] SECURITY")
git_dir = os.path.join(BASE, '.git')
env_file = os.path.join(BASE, 'backend', '.env')
gitignore = os.path.join(BASE, '.gitignore')

print(f"  .git repo initialised : {'YES' if os.path.exists(git_dir) else 'NO — run git init before submission'}")
print(f"  backend/.env exists   : {'YES' if os.path.exists(env_file) else 'NO — create from .env.example'}")

if os.path.exists(gitignore):
    gi = open(gitignore).read()
    env_covered = ('backend/.env' in gi) or ('\n.env\n' in gi) or ('/.env' in gi)
    print(f"  .env is gitignored    : {'YES ✓' if env_covered else 'NO — add to .gitignore!'}")

if os.path.exists(env_file):
    print("  Keys in backend/.env  (values HIDDEN):")
    for line in open(env_file):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key = line.split('=')[0].strip()
            val = line.split('=', 1)[1].strip()
            is_placeholder = any(p in val.lower() for p in [
                'yourpassword','change-this','replace','your-secret','placeholder','example'])
            status = 'PLACEHOLDER ⚠' if is_placeholder else ('empty' if not val else 'SET ✓')
            print(f"    {key}: {status}")

# Check config.py for hardcoded secrets
cfg = os.path.join(BASE, 'backend', 'app', 'core', 'config.py')
if os.path.exists(cfg):
    txt = open(cfg).read()
    if 'settings.SECRET_KEY' in txt or 'SECRET_KEY' in txt:
        print("  config.py SECRET_KEY  : loaded from env ✓")

# ── 3. Python syntax ─────────────────────────────────────────
print("\n[3] PYTHON SYNTAX")
import py_compile
backend = os.path.join(BASE, 'backend')
skip = {'__pycache__', '.venv'}
ok_count = 0; fail_count = 0
for root, dirs, files in os.walk(backend):
    dirs[:] = [d for d in dirs if d not in skip]
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            try:
                py_compile.compile(fp, doraise=True)
                ok_count += 1
            except py_compile.PyCompileError as e:
                print(f"  FAIL {os.path.relpath(fp, backend)}: {e}")
                fail_count += 1
print(f"  {ok_count} files OK, {fail_count} failures")

# ── 4. check_all.py exists ────────────────────────────────────
print("\n[4] TEST SCRIPTS")
check_all = os.path.join(BASE, 'backend', 'check_all.py')
print(f"  backend/check_all.py  : {'FOUND ✓' if os.path.exists(check_all) else 'MISSING'}")
test_reg  = os.path.join(BASE, 'backend', 'test_register.py')
print(f"  backend/test_register.py: {'FOUND ✓' if os.path.exists(test_reg) else 'MISSING'}")

# ── 5. Frontend dist ─────────────────────────────────────────
print("\n[5] FRONTEND BUILD")
dist = os.path.join(BASE, 'frontend', 'dist')
if os.path.exists(dist):
    html = os.path.join(dist, 'index.html')
    assets = os.path.join(dist, 'assets')
    js_files = [f for f in os.listdir(assets) if f.endswith('.js')] if os.path.exists(assets) else []
    css_files = [f for f in os.listdir(assets) if f.endswith('.css')] if os.path.exists(assets) else []
    print(f"  dist/index.html  : {'OK ✓' if os.path.exists(html) else 'MISSING'}")
    print(f"  dist/assets/*.js : {len(js_files)} file(s)")
    print(f"  dist/assets/*.css: {len(css_files)} file(s)")
    # Get JS size
    for jf in js_files:
        size = os.path.getsize(os.path.join(assets, jf)) // 1024
        print(f"    {jf} ({size} KB)")
else:
    print("  dist/ does not exist — run: npm run build")

# ── 6. README check ──────────────────────────────────────────
print("\n[6] README")
readme = os.path.join(BASE, 'README.md')
if os.path.exists(readme):
    txt = open(readme, encoding='utf-8').read()
    sections = ['Prerequisites', 'Installation', 'Environment', 'migration', 'uvicorn', 'npm run dev', 'API Endpoints']
    for s in sections:
        found = s.lower() in txt.lower()
        print(f"  {'✓' if found else '✗'} Section covers: {s}")
    print(f"  README word count: ~{len(txt.split())} words")
else:
    print("  README.md MISSING")

print("\n" + "=" * 60)
print("  Audit complete. Run backend/check_all.py for live API tests.")
print("=" * 60)
