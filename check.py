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

print()
for ok, label, detail in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:34} {detail}")
failed = sum(1 for ok, _, _ in results if not ok)
print(f"\n  {len(results) - failed}/{len(results)} passing\n")
sys.exit(1 if failed else 0)
