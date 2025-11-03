from flask import Blueprint, render_template

bp = Blueprint('signin', __name__, url_prefix='/')

@bp.route('/signin', methods=('GET', 'POST'))
def signin():
    """signin page for retroNet"""
    db = get_db()
    posts = db.execute(
        'SELECT username'
        ' FROM user'
    ).fetchall()
    return render_template('user/profile.html')