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

## 2026-10-10: Lesson 2.3 housekeeping (invites)

- **Schema change: `invite.created_by` can now be NULL.** It used to be `NOT NULL`, which meant every invite needed an existing user to create it, so a brand-new site could never get its first member. NULL now means "created by the site admin from the command line."
  - **This needs a database reset.** `init_db()` only creates tables that are *missing* (`CREATE TABLE IF NOT EXISTS`). It never changes a table that already exists, so your current DB still has the old `NOT NULL` rule. Lesson 2.3, step 0 walks through the reset. The general lesson: once you have real users, a schema change needs a *migration* (an `ALTER TABLE` script), not a reset.
- **New `retroApp/models/invite.py`** with `create_invite()` and a `create-invite` command. Registered in `__init__.py`.
- **New `retronet/manage.sh`** runs Flask's command line without having to remember `--app 'retroApp:create_retroNet()'`. Try `retronet/manage.sh create-invite` or `retronet/manage.sh --help`.
- **Fixed `init-db` (and the new command) to run inside an app context.** A plain `@click.command` added with `app.cli.add_command()` doesn't get one, so `get_db()` crashed with "Working outside of application context." `@with_appcontext` fixes it.
- **`start.sh` and `manage.sh` now use an absolute path to the venv,** which silences the `Unexpected value in sys.prefix` warning caused by running `../bin/python`.
- **`check.py` now uses real invite codes for its test signups** and has three invite tests.

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
- [x] The invite key is never validated against the `invite` table.
- [x] Signup crashes with a 400 if the `key` field is missing, and it accepts a blank email. (Lesson 2.4 also added username/password rules, duplicate-account messages, and a uniform sign-in error.)
- [ ] `create.py` still reads fields with `request.form[...]` (400 on a missing field) and wraps everything in a catch-all `except`.
- [ ] The signup form's `display` field is never saved.
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

---

## Planned features

Not started yet. These are bigger pieces of work, not bug fixes.

- [ ] **Landing page CSS rewrite for cross-browser rendering.** The landing page renders differently in Chromium-based browsers and Firefox. Rewrite its CSS so it looks the same in both.
- [ ] **Customizable site-wide themes.** Much of this was already built in earlier chats, and that code will be brought in here as the starting point.
  - **Every section has its own theme** (landing page, Usenet, neighborhood, etc.), and each section offers its own set of premade, built-in themes.
  - **A theme dropdown** sits at the top left or right. Visitors choose which built-in theme they see for each section, e.g. a different landing page theme.
  - **Preferences are stored in a cookie,** so you don't need an account to try out themes. This depends on the cookie consent popup: if a visitor declines cookies, their choice only lasts for the current page view.
  - **No custom themes for the main sections.** Users can design their own themes only for their home page, personal website, and BlinkShine animation/game pages.
  - **Community theme competitions.** The winner's theme is added to the built-in list.
- [ ] **Cookie consent popup.** Small, unintrusive, retro-styled, and closable. It exists only to save personal preferences such as themes. Visitors are free to accept or decline. Cookie use is transparent: a short page lists every cookie and what it does, linked to the open source code. The login session cookie is strictly necessary and works whether or not they accept, so declining doesn't stop anyone signing in.
- [ ] **Donations page.** A page has already been generated in another chat and will be brought in. The work is wiring it into the app: route, template, nav link, and matching the active theme.
- [ ] **Run Hypercorn under Gunicorn.** Write a Gunicorn worker class that runs Hypercorn:
  - Gunicorn manages the processes: spawning, restarting dead workers, graceful reloads, and a real worker count.
  - Each worker runs Hypercorn's `serve()` on the sockets Gunicorn hands it, so Hypercorn's protocol support is kept.
  - Gunicorn's heartbeat is wired into the worker's event loop so a hung worker gets noticed and replaced.
  - `serve()` gets a `shutdown_trigger` tied to Gunicorn's signals, so shutdowns and reloads are clean.
  - Estimated at 100–200 lines. It doesn't need to be a fork of either project; it can be a small separate package. Uvicorn's `UvicornWorker` follows the same pattern and is a useful reference.
  - This also fixes the backlog item above where `run.py` sets `config.workers` but only one worker actually runs.
- [ ] **Fix CSS animation performance.** The animations slow pages down. Find what's causing the slowdown and fix it while keeping every animation.
- [ ] **Replace hardcoded front-page data with real data.** The front page shows made-up content. Pull it from the database instead. (Related to the lesson 3 backlog item about `get_user_profile()` inventing data.)
- [ ] **Fix the visitor counter.** It's buggy and needs work.
- [ ] **Add old-web features, starting with a webring.** The webring connects the websites of all your projects, with retroNet as one of its members.
- [ ] **Set up an email server.** *Needed for alpha testers.* The server will also handle mail for other websites that have nothing to do with retroNet, so the setup has to plan for multiple domains from the start: per-domain sending identities and SPF/DKIM/DMARC records, and keeping retroNet's config separate from the other sites'.
- [ ] **Email notifications to users.** *Needed for alpha testers. Depends on the email server.* Email verification at signup, post notifications, and similar.
- [ ] **User blogs on profile pages.** A blog on each user's home page. Their stalkers can read posts, comment, and leave emoji reacts (thumbs up, heart, etc.).
  - **Reacts on reacts.** Users can react to a react. If someone likes a blog post, someone else can like that like, and so on, forming a tree up to 256 levels deep.
  - **Assess database usage** for nesting that deep: how the tree is stored (e.g. parent pointer + depth column vs. a closure table), how deep chains are queried without recursive-query blowups, and how storage grows.
  - **Protect against exploits:** enforce the 256-level cap on the server, rate-limit reacts, allow one react per user per node, and stop bots or scripts from flooding deep chains to bloat the DB.
- [ ] **Custom user websites in MTHL (Manic Text Hyperlink Language).** Users can build their own sites in MTHL or choose from several premade themes. Earlier chats on both will be saved here as the starting point. *Depends on the MTHL interpreter.*
- [ ] **Personal websites section.** A separate area of the site for users' personal websites, organized into themed neighborhoods/categories in the style of the old personal-homepage directories (e.g. "Area 51" for conspiracy theories). Sites are built in MTHL.
- [ ] **Build the MTHL interpreter.** It turns MTHL into HTML. It is deliberately **Turing-incomplete** for security, so a user's page can't hang the server or run arbitrary code. It has loops for churning out repeated patterns, but every loop is bounded and finite: no indefinite or ongoing looping, and the cap is low, since websites only have a few repeating patterns. Its output still needs sanitizing so users can't inject scripts or styles into other people's pages.
- [ ] **Incorporate BlinkShine.** *Depends on the BlinkShine alpha being ready.* BlinkShine is a separate project: an HTML5-based replacement for Macromedia Flash.
  - A separate part of retroNet where users create their own animations, movies and games, the way they did with Flash.
  - Users can embed their BlinkShine creations in their MTHL personal websites once it's ready.
- [ ] **Reach out to Neocities about collaborating.**
  - **If they're willing:** use the Neocities API to connect retroNet to Neocities.
  - **If not:** ask whether they'd join a webring instead (see the webring item above).

### Nav bar links

The top nav is copy-pasted in two places: `templates/user_base.html` (line 39) and `templates/user/retronet_user_page.html` (line 348). Every change below has to be made in both, or the nav could move into one shared include first.

- [ ] **Unify the nav bar across the whole site.** One shared template (e.g. a `nav.html` include) that every page uses, so a link change happens in one place. Do this first; it makes the rest of this list easier.
- [ ] **Add the nav bar to Usenet.** The Usenet pages (`usenet_base.html`) don't have it yet. This comes for free once the nav is unified.
- [ ] **Browse** (`/browse`): work out what it should be and whether it's needed at all.
- [ ] **Remove Forums** (`/forums`). The profile feed also has a `forum` item type and the text "Subscribe to forums and Usenet groups" (`user/profile.html` and `user/retronet_user_page.html`), so clean those up too.
- [ ] **Add "Neighborhood"** linking to the personal websites section.
- [ ] **Add "Animation"** linking to the BlinkShine section.
- [ ] **Build the search feature** (`/search`).
- [ ] **Point "My Profile" at the signed-in user's own profile.** It currently links to a fixed `/profile`.
- [ ] **Change / forgot password.** Changing it while signed in, plus a reset for a forgotten password. The forgotten-password reset depends on the email server and notifications.

### Usenet

- [ ] **Make the Usenet menu bar work.** File, Edit, View, Message and Help (`templates/usenet_base.html:39`) are currently plain `<div>`s that do nothing. Turn them into real, interactive drop-down menus.
  - **CSS first, light JavaScript only if needed.** Drop-downs can open on click with no JS using `<details>`/`<summary>` or `:focus-within`, with CSS animations for the opening and closing. Use JS only for things CSS can't do, such as closing a menu when you click outside it or arrow-key navigation.
  - **Keyboard accessible:** menus open with Enter/Space and close with Escape.
  - **Possible menu contents** (suggestions, to be decided):
    - **File:** New Message, Subscribe to group, Print, Exit to retroNet.
    - **Edit:** Find in message, Select all.
    - **View:** Threaded / flat sort, Show read / unread, Theme.
    - **Message:** New, Reply, Forward, Next, Mark as read.
    - **Help:** About, Usenet etiquette, Keyboard shortcuts.
- [ ] **Make the toolbar buttons work too.** Get Msg, New Msg, Reply, Forward, File, Next, Print and Delete (line 48) are also dead buttons. Several overlap with the menus, so the menus and buttons should share the same actions. Depends on the Usenet section reading real data (see the `dummy.py` backlog item).

### Profiles

- [ ] **Show each user's member number on their home page.** Use `user.id` from the database as the public member number, e.g. "Member #42".
  - **It's already sequential.** `user.id` is `INTEGER PRIMARY KEY AUTOINCREMENT` in `schema.sql`, so the first user is 1, the next is 2, and so on. With `AUTOINCREMENT`, SQLite never reuses an id, even after an account is deleted.
  - **Gaps are normal.** A deleted account leaves a hole that never gets refilled. So member numbers are always in signup order but not always consecutive.
  - **A DB reset restarts the count at 1.** Before alpha, that's fine. After real users join, numbers have to survive migrations and backups.
  - **Trade-off to accept:** sequential numbers show how many accounts exist and the order people joined. That's part of the retro charm here, but it means nothing secret should rely on an id being hard to guess. Ownership checks always use the logged-in session, never the id in the URL.

### Infrastructure

- [ ] **Plan the migration from SQLite to PostgreSQL as the site grows.** Not urgent yet. Two decisions to make later: *when* to migrate, and *when to start nudging the codebase in that direction*.
  - **Possible triggers for migrating:**
    - Write contention. SQLite allows only one writer at a time, so once Gunicorn runs several workers (see the Gunicorn item), busy reacts, comments and visitor counting will queue behind each other and you'll start seeing "database is locked" errors.
    - Running on more than one server.
    - The DB getting large or busy enough to need proper concurrent access, roles, or online backups.
  - **Architectural choices to make:**
    - How the app talks to the DB: keep raw SQL with a thin helper (today's style), or adopt a query layer such as SQLAlchemy Core that runs on both SQLite and Postgres.
    - Sync vs. async driver (`psycopg` vs. `asyncpg`), which matters because the app runs on Hypercorn.
    - A schema migration tool (e.g. Alembic) instead of `init_db()` plus resets. You'll need this either way once there are real users (see the Lesson 2.3 note).
    - How to move existing data across (e.g. `pgloader`, or a one-off export/import script).
  - **Cheap prep that can start any time** and keeps the move easy:
    - Keep all SQL inside `models/`, not scattered across views.
    - Avoid SQLite-only SQL where there's a portable equivalent. Watch for `?` placeholders (Postgres drivers use `%s`), `AUTOINCREMENT` (Postgres uses `GENERATED ... AS IDENTITY`), `INSERT OR IGNORE`, and loose typing (SQLite will store text in an integer column; Postgres won't).
    - Write tests against the model functions so the same tests can later run against Postgres.
  - **Knock-on effect on member numbers:** Postgres sequences *do* use up numbers on failed inserts and rolled-back transactions, so after the move there will be more gaps in member numbers than there are now. The migration must also carry existing ids over unchanged and reset the sequence to continue after the highest one.
