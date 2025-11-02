from flask import Blueprint, render_template

bp = Blueprint('usenet', __name__)

@bp.route('/usenet', methods=('GET', 'POST'))
def usenet():
    """Main usenet page for retroNet"""
    return render_template('usenet/groups.html')