from flask import Blueprint, render_template

bp = Blueprint('signin', __name__, url_prefix='/')

@bp.route('/signin', methods=('GET', 'POST'))
def signin():
    """signin page for retroNet"""
    return render_template('auth/signin.html')