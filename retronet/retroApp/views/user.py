from flask import Blueprint, render_template

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/<username>')
def profile(username):
    """User profile page for retroNet"""
    return render_template('user/profile.html', username=username)