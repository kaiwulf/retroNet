import functools

from flask import (
    Blueprint, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from retroApp.models.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password required'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already signuped"
            else:
                return redirect(url_for("auth.signin"))
        # flush(error)
    return render_template('auth/signup.html')

@bp.route('/signin', methods=('GET','POST'))
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # new_password = request.form['new-password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        # This code will be for updating password in a new page in auth/
        # elif new_password:
        #     try:
        #         db.execute(
        #             "UPDATE user SET password = ? WHERE username = ?", (generate_password_hash(new_password), username)
        #         )
        #         db.commit()
        #     except db.IntegrityError:
        #         error = f"Error changing password"
        #     else:
        #         return redirect(url_for("auth.login"))
        # if password is not None:
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'
        else:
            print(f"password empty")

        print(f"error: {error}")
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('user.profile'))

        # flush(error)
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
    return redirect(url_for('landing.landing'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

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