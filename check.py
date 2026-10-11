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

def check(label, fn, want=200):
    try:
        got = fn()
    except Exception as exc:
        results.append((False, label, f"{type(exc).__name__}: {exc}"))
    else:
        results.append((got == want, label, f"{got} (want {want})"))

# seed two users so the profile pages have something to render
client.post("/auth/signup", data=dict(username="alice", password="pw", email="a@x.com", key="123"))
client.post("/auth/signup", data=dict(username="bob", password="pw", email="b@x.com", key="123"))

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

def signed_in_as(username, password="pw"):
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
    c.post("/auth/signup", data=dict(username="carol", password="pw", email="c@x.com", key="123"))
    r = c.post("/create/carol", data=dict(PROFILE, display="Carol"))
    return r.headers.get("Location") if display_name_of("carol") == "Carol" else "profile not saved"

check("L2 anonymous edit -> sent to sign in", anon_edit,       want="/auth/signin")
check("L2 bob edits alice -> 403",           bob_edits_alice, want=403)
check("L2 alice edits alice -> saved",       alice_edits_alice, want="/user/alice")
check("L2 new signup can create profile",    fresh_signup_can_create_profile, want="/user/carol")

print()
for ok, label, detail in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:34} {detail}")
failed = sum(1 for ok, _, _ in results if not ok)
print(f"\n  {len(results) - failed}/{len(results)} passing\n")
sys.exit(1 if failed else 0)
