# retroNet change log

A record of significant changes, so you know what moved and why.
Small tweaks (a missing import, a typo) are not listed here.

---

## 2026-10-10: Cleanup pass 1

### Environment

**Virtualenv rebuilt.** Arch upgraded the system Python from 3.13 to 3.14. The
old venv's `bin/python` was a symlink to the system Python, but its packages
lived in `lib/python3.13/`, so nothing could be imported and the app would not
start. The venv was deleted and rebuilt with `python3 -m venv .`, then
reinstalled from `retronet/requirements.txt`.

- **What changes for you:** nothing day to day. If Python gets upgraded again
  and imports start failing, rebuild it the same way:
  ```sh
  rm -rf bin lib lib64 pyvenv.cfg
  python3 -m venv .
  git checkout -- .gitignore        # venv overwrites it with "*"
  ./bin/pip install -r retronet/requirements.txt
  ```
- **Watch out:** `python3 -m venv .` overwrites `.gitignore` with a file that
  just says `*`. That happened during this rebuild and the file was restored
  from git. Moving the venv into its own folder (e.g. `.venv/`) would avoid
  this. That's a recommendation and hasn't been done.

**`start.sh` now actually starts the app.** It used to contain only
`source ../bin/activate`, which does nothing useful when you run a script.
Run `retronet/start.sh` from any directory and the server comes up on port 65000.

### Database

**The SQLite file is no longer tracked by git.** `var/retroApp-instance/retroNet.sqlite`
was removed from the git index with `git rm --cached`. The file itself is still
on disk and the app still uses it. `var/` was added to `.gitignore`.

- **Why:** a database is runtime data, not source code. Committing it means
  every signup creates a binary diff, and real users' password hashes and
  emails end up in git history.
- **Where the DB lives:** Flask picks `var/retroApp-instance/` because the
  venv root is the repo root. Your app package therefore sits under
  `sys.prefix`, and Flask treats it as an installed package. Print
  `app.instance_path` if you ever need to confirm it.
- **Backup:** a copy of the DB as it was on 2026-10-10 is in the Claude
  scratchpad. It's temporary, so copy it somewhere permanent if you want to keep it.
- **Still to do:** you chose to start with a fresh DB. The old one, with
  accounts kai / kaiwulf / folkwulf, hasn't been reset yet. To reset it, stop the
  server, delete `var/retroApp-instance/retroNet.sqlite`, and start the app.
  `init_db()` recreates every table on boot.

### Code

| File | Change | Why |
|---|---|---|
| `retroApp/__init__.py` | Removed unused imports (`jsonify`, `request`, `asyncio`, `httpx`, `aiosqlite`, `wraps`). | Dead imports make it harder to tell what the file depends on. |
| `retroApp/__init__.py` | `init_db()` no longer sits in a `try/except` that printed "Database already exists or error". | The schema uses `CREATE ... IF NOT EXISTS`, so it is safe to run on every boot. The old `except` would have hidden a real schema error behind a misleading message. |
| `retroApp/articles.py` | `render_template('index.html')` became `'usenet/index.html'`, and the same for `post.html`. | The templates live in `templates/usenet/`. Template paths are always relative to `templates/`, never to the blueprint. |
| `retroApp/articles.py` | `url_for('index')` became `url_for('usenet.usenet')`. | No endpoint called `index` ever existed. |
| `retroApp/articles.py` | Added `build_categories()`, replacing two copy-pasted loops. | You'll use it in the usenet lesson. |
| `retroApp/articles.py` | Removed the `/demo/quotes` and `/demo/preview` routes. | Their templates don't exist, so both returned a 500. |
| `views/user/user.py` | Added the missing `abort` import. | `/user/<unknown>` crashed with `NameError` instead of returning a 404. |

### Deleted files (dead code)

All of these were tracked in git, so `git checkout 2c4f053 -- <path>` brings any of them back.

| File | Why it was dead |
|---|---|
| `views/auth/signin.py` | A second `signin` blueprint that was never registered. Every `url_for('auth.signin')` points at `auth.py`. |
| `views/auth/signup.py` | Same situation, a duplicate of the signup in `auth.py`. |
| `retroApp/app_example.py` | A standalone example of template filters. The real ones are in `template_filters.py`. |
| `models/schema.sql.old` | An old schema. The live one is `schema.sql`. |
| `views/auth/user/` | Empty, untracked folder. |

### Added files

- **`__init__.py`** in `views/`, `views/auth/`, `views/user/`, `views/usenet/`,
  `models/` and `models/user/`. These folders used to work only as implicit
  "namespace packages". An `__init__.py` marks a folder as a normal Python
  package. That's the conventional layout, and it rules out confusing import
  shadowing.
- **`check.py`** (repo root) is a self-test that hits the routes being fixed.
  Run it with `./bin/python check.py`. It uses a throwaway database, so your
  real data is never touched.

---

## 2026-10-10: Lesson 2.2 housekeeping

- **Deleted `retronet/config.py`** (empty file). It looked like the app's config file, but it was never loaded. `create_retroNet()` calls `app.config.from_pyfile('config.py')`, and because the app uses `instance_relative_config=True`, that path is relative to the **instance folder**: `var/retroApp-instance/config.py`. Your real config (secret key and so on) goes there. That folder is gitignored, so secrets never get committed.
- **Added `lessons/`** to hold small demo scripts used in lessons. `lessons/forge_cookie.py` forges a login cookie from a known secret key, to show why the key matters. It's safe to delete any time.
- **`check.py`** now also checks that the app refuses to start without a `SECRET_KEY`, and that your real config's key is strong.

---

## Known issues backlog

These are verified but not yet fixed. Lessons will work through them roughly in this order.

**Crashes: lesson 1, done 2026-10-10 (`check.py` 7/7)**
- [x] `get_stalkers()` closes the shared DB connection. Every profile page breaks once anyone follows anyone.
- [x] `usenet_base.html` calls the `render_thread` macro before defining it.
- [x] `usenet_base.html` links `style.css`, which doesn't exist. It should be `css/usenet.css`.
- [x] The `/usenet` view passes none of the variables its template needs.
- [ ] `/auth/backend` renders `auth/backend.html` (which doesn't exist) and queries a `post` table (which also doesn't exist).

**Security: lesson 2, required before real users**
- [x] `SECRET_KEY='dev'` is hardcoded, so anyone can forge a login cookie.
- [x] `/create/<username>` has no login or ownership check. Anyone can overwrite anyone's profile.
- [ ] The invite key is never validated against the `invite` table.
- [ ] Signup crashes with a 400 if the `key` field is missing, and it accepts a blank email.
- [ ] Werkzeug 3.0.0 is pinned and has published security advisories. Upgrade it.

**Fake data shown to real users: lesson 3**
- [ ] `get_user_profile()` invents stalkers, comments, blog posts and a feed, and hardcodes `location='Texas'`, `age=22` and `website` onto every profile. It also overwrites the real `created_at`.

**Smaller bugs**
- [ ] `create_user()` has 3 columns but 2 `?` placeholders, and uses a `key` column that doesn't exist. It's currently unused.
- [ ] `update_profile_music()` and `landing.get_active_songs()` use a `profile_music` column that doesn't exist.
- [ ] `get_users_music_list()` raises `UnboundLocalError` if its query fails.
- [ ] `run.py` sets `config.workers`, but Hypercorn's `serve()` ignores it. Only one worker runs.
- [ ] The usenet section still reads from `dummy.py`, not from the `usenet_group` and `usenet_post` tables.
- [ ] Lots of leftover debug `print()` calls (`pprint` of the whole profile, including the password hash).
