import functools
import re
from retroApp.models.invite import claim_invite

from flask import (
    Blueprint, g, redirect, render_template, request, flash, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from retroApp.models.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
USERNAME_RE = re.compile(r'[a-z0-9_-]{3,20}')

@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        key = request.form.get('key', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        db = get_db()
        error = None

        if not USERNAME_RE.fullmatch(username):
            error = 'Usernames are 3-20 characters: letters, numbers, _ and - only.'
        elif '@' not in email:
            error = 'Please enter a valid email address.'
        elif not key:
            error = 'An invite key is required.'
        elif len(password) < 8:
            error = 'Passwords must be at least 8 characters.'
        elif password != confirm:
            error = 'The two passwords do not match.'
        
        if error is None:
            try:
                cursor = db.execute(
                    "INSERT INTO user (username, password, email, invite_key) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password), email, key),
                )
                new_user_id = cursor.lastrowid

                if not claim_invite(key, new_user_id):
                    db.rollback()
                    flash('That invite key is invalid or has already been used.')
                    return render_template('auth/signup.html')
                db.commit()
                session.clear()
                session['user_id'] = new_user_id
                flash('Account created! Now set up your profile.')
                return redirect(url_for("create.new_profile", username=username))
            except db.IntegrityError as e:
                db.rollback()
                if 'user.username' in str(e):
                    error = 'That username is already taken.'
                elif 'user.email' in str(e):
                    error = 'An account with that email already exists.'
                else:
                    raise

        flash(error)
    return render_template('auth/signup.html')

@bp.route('/signin', methods=('GET','POST'))
def signin():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            error = 'Incorrect username or password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            print(f"Going to user.profile")
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('user.profile', username=username))
        flash(error, 'error')
    return render_template('auth/signin.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('landing.landing'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.signin'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/backend')
def backend():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('auth/backend.html', posts=posts)