"""Quick self-check: exercises the routes that are currently broken.

Run from the repo root:   ./bin/python check.py
It uses a throwaway database, so your real data in var/ is never touched.
"""
import os, sqlite3, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "retronet"))
from retroApp import create_retroNet

db_path = os.path.join(tempfile.mkdtemp(), "check.sqlite")
app = create_retroNet({"SECRET_KEY": "test", "DATABASE": db_path, "TESTING": True})
client = app.test_client()

results = []

PASSWORD = "retro-pass-123"
PW = dict(password=PASSWORD, confirm_password=PASSWORD)

def new_invite():
    """Create a real, unused invite code in the test database."""
    from retroApp.models.invite import create_invite
    with app.app_context():
        return create_invite()

def check(label, fn, want=200):
    try:
        got = fn()
    except Exception as exc:
        results.append((False, label, f"{type(exc).__name__}: {exc}"))
    else:
        results.append((got == want, label, f"{got} (want {want})"))

# seed two users so the profile pages have something to render
client.post("/auth/signup", data=dict(username="alice", **PW, email="a@x.com", key=new_invite()))
client.post("/auth/signup", data=dict(username="bob", **PW, email="b@x.com", key=new_invite()))

check("GET /usenet renders",          lambda: client.get("/usenet").status_code)
check("GET /user/alice",              lambda: client.get("/user/alice").status_code)
check("GET /user/ghost -> 404",       lambda: client.get("/user/ghost").status_code, want=404)
check("GET /group/1 (has articles)",  lambda: client.get("/group/1").status_code)
check("GET /article/1",               lambda: client.get("/article/1").status_code)

# url_for() never checks that a static file exists, so a wrong stylesheet path
# renders the page fine (200) and only 404s when the browser fetches the CSS.
def usenet_stylesheet_status():
    import re
    html = client.get("/usenet").get_data(as_text=True)
    match = re.search(r'<link rel="stylesheet" href="([^"]+)"', html)
    return client.get(match.group(1)).status_code if match else "no <link> tag"
check("usenet stylesheet actually loads", usenet_stylesheet_status)

# the regression that only appears once somebody follows somebody
con = sqlite3.connect(db_path)
con.execute("INSERT INTO stalker (stalker_id, stalked_id) VALUES (2, 1)")
con.commit(); con.close()
check("GET /user/alice WITH a follower", lambda: client.get("/user/alice").status_code)

# ── Lesson 2: who may edit a profile? ─────────────────────────────────────
PROFILE = dict(display="X", track="t", artist="a", album="b", bio="b")

def display_name_of(username):
    con = sqlite3.connect(db_path)
    row = con.execute("SELECT display_name FROM user WHERE username = ?", (username,)).fetchone()
    con.close()
    return row[0] if row else None

def signed_in_as(username, password=PASSWORD):
    c = app.test_client()
    c.post("/auth/signin", data=dict(username=username, password=password))
    return c

def anon_edit():
    before = display_name_of("alice")
    r = app.test_client().post("/create/alice", data=dict(PROFILE, display="HACKED BY ANON"))
    if display_name_of("alice") != before:
        return "profile was overwritten!"
    return r.headers.get("Location")

def bob_edits_alice():
    before = display_name_of("alice")
    r = signed_in_as("bob").post("/create/alice", data=dict(PROFILE, display="HACKED BY BOB"))
    if display_name_of("alice") != before:
        return "profile was overwritten!"
    return r.status_code

def alice_edits_alice():
    r = signed_in_as("alice").post("/create/alice", data=dict(PROFILE, display="Alice"))
    return r.headers.get("Location") if display_name_of("alice") == "Alice" else "edit did not save"

def fresh_signup_can_create_profile():
    c = app.test_client()   # signs up, then goes straight to profile creation, no separate sign-in
    c.post("/auth/signup", data=dict(username="carol", **PW, email="c@x.com", key=new_invite()))
    r = c.post("/create/carol", data=dict(PROFILE, display="Carol"))
    return r.headers.get("Location") if display_name_of("carol") == "Carol" else "profile not saved"

check("L2 anonymous edit -> sent to sign in", anon_edit,       want="/auth/signin")
check("L2 bob edits alice -> 403",           bob_edits_alice, want=403)
check("L2 alice edits alice -> saved",       alice_edits_alice, want="/user/alice")
check("L2 new signup can create profile",    fresh_signup_can_create_profile, want="/user/carol")

# ── Lesson 2.2: the secret key ────────────────────────────────────────────
def refuses_to_start_without_key():
    try:
        create_retroNet({"DATABASE": os.path.join(tempfile.mkdtemp(), "k.sqlite"), "TESTING": True})
    except RuntimeError:
        return "refused"
    except Exception as exc:
        return f"crashed with {type(exc).__name__}, not RuntimeError"
    return "started anyway (fell back to a default key)"

def real_config_key_is_strong():
    import runpy
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "var", "retroApp-instance", "config.py")
    if not os.path.exists(path):
        return "var/retroApp-instance/config.py does not exist"
    key = runpy.run_path(path).get("SECRET_KEY")
    if not key:
        return "config.py has no SECRET_KEY"
    if key == "dev" or len(key) < 32:
        return "SECRET_KEY is too short or guessable"
    return "strong"

check("L2 no SECRET_KEY -> refuses to start", refuses_to_start_without_key, want="refused")
check("L2 real config has a strong key",      real_config_key_is_strong,    want="strong")

# ── Lesson 2.3: invite keys ───────────────────────────────────────────────
def user_exists(username):
    con = sqlite3.connect(db_path)
    found = con.execute("SELECT 1 FROM user WHERE username = ?", (username,)).fetchone()
    con.close()
    return found is not None

def bogus_invite_rejected():
    r = app.test_client().post("/auth/signup", data=dict(username="dave", **PW, email="d@x.com", key="TOTALLY-INVALID"))
    if user_exists("dave"):
        return "account was created"
    return "rejected" if r.status_code == 200 else f"status {r.status_code}"

def valid_invite_gets_used():
    code = new_invite()
    app.test_client().post("/auth/signup", data=dict(username="erin", **PW, email="e@x.com", key=code))
    con = sqlite3.connect(db_path)
    user = con.execute("SELECT id FROM user WHERE username = 'erin'").fetchone()
    used_by = con.execute("SELECT used_by FROM invite WHERE invite_code = ?", (code,)).fetchone()[0]
    if not user:
        return "account was not created"
    return "marked used" if used_by == user[0] else f"invite.used_by is {used_by!r}, want {user[0]}"

def reused_invite_rejected():
    code = new_invite()
    app.test_client().post("/auth/signup", data=dict(username="frank", **PW, email="f@x.com", key=code))
    r = app.test_client().post("/auth/signup", data=dict(username="grace", **PW, email="g@x.com", key=code))
    if user_exists("grace"):
        return "second account was created with the same code"
    return "rejected" if r.status_code == 200 else f"status {r.status_code}"

check("L2 bogus invite -> no account",  bogus_invite_rejected,  want="rejected")
check("L2 valid invite -> marked used", valid_invite_gets_used, want="marked used")
check("L2 reused invite -> no account", reused_invite_rejected, want="rejected")

# ── Lesson 2.4: input validation ──────────────────────────────────────────
def user_count():
    con = sqlite3.connect(db_path)
    n = con.execute("SELECT COUNT(*) FROM user").fetchone()[0]
    con.close()
    return n

_signup_attempts = iter(range(1000))

def rejected(**fields):
    """Submit signup with valid values, overridden by `fields`, and expect no new account."""
    n = next(_signup_attempts)
    data = dict(username=f"tester{n}", email=f"tester{n}@x.com", key=new_invite(), **PW)
    data.update(fields)
    data = {k: v for k, v in data.items() if v is not None}     # None = leave the field out entirely
    before = user_count()
    r = app.test_client().post("/auth/signup", data=data)
    html = r.get_data(as_text=True)
    if user_count() != before:
        return "account was created"
    if r.status_code != 200:
        return f"status {r.status_code} (should re-show the form with a message)"
    if "constraint" in html.lower() or "IntegrityError" in html:
        return "shows a raw database error to the user"
    return "rejected"

def invite_survives_failed_signup():
    code = new_invite()
    app.test_client().post("/auth/signup", data=dict(username="ivy", email="i@x.com", key=code,
                                                     password=PASSWORD, confirm_password="different"))
    con = sqlite3.connect(db_path)
    used_by = con.execute("SELECT used_by FROM invite WHERE invite_code = ?", (code,)).fetchone()[0]
    con.close()
    return "unused" if used_by is None else "invite was used up by a failed signup"

def signin_errors_identical():
    wrong_user = app.test_client().post("/auth/signin", data=dict(username="nobody", password=PASSWORD))
    wrong_pass = app.test_client().post("/auth/signin", data=dict(username="alice", password="wrong-password"))
    return "identical" if wrong_user.get_data() == wrong_pass.get_data() else "page differs: reveals which usernames exist"

def signin_case_insensitive():
    r = app.test_client().post("/auth/signin", data=dict(username="  ALICE ", password=PASSWORD))
    return r.headers.get("Location") or f"status {r.status_code}"

check("L2 signup: invite field missing",  lambda: rejected(key=None),                     want="rejected")
check("L2 signup: blank email",           lambda: rejected(email=""),                     want="rejected")
check("L2 signup: email without @",       lambda: rejected(email="not-an-email"),         want="rejected")
check("L2 signup: username with /",       lambda: rejected(username="a/b"),               want="rejected")
check("L2 signup: username too short",    lambda: rejected(username="ab"),                want="rejected")
check("L2 signup: password under 8",      lambda: rejected(password="short", confirm_password="short"), want="rejected")
check("L2 signup: passwords differ",      lambda: rejected(confirm_password="something-else"), want="rejected")
check("L2 signup: username taken",        lambda: rejected(username="alice"),             want="rejected")
check("L2 signup: 'Alice' when alice exists", lambda: rejected(username="Alice"),         want="rejected")
check("L2 signup: email taken",           lambda: rejected(email="a@x.com"),              want="rejected")
check("L2 failed signup keeps invite",    invite_survives_failed_signup,                  want="unused")
check("L2 signin: same error either way", signin_errors_identical,                        want="identical")
check("L2 signin: ignores case/spaces",   signin_case_insensitive,                        want="/user/alice")
check("L2 signin: field missing -> no 400", lambda: app.test_client().post("/auth/signin", data=dict(username="alice")).status_code, want=200)

print()
for ok, label, detail in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:34} {detail}")
failed = sum(1 for ok, _, _ in results if not ok)
print(f"\n  {len(results) - failed}/{len(results)} passing\n")
sys.exit(1 if failed else 0)
