from flask import Blueprint, render_template

bp = Blueprint('signup', __name__, url_prefix='/')

@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    """signup page for retroNet"""
    return render_template('auth/signup.html')