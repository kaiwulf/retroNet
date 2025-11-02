from flask import Blueprint, render_template

bp = Blueprint('landing', __name__)

@bp.route('/')
def landing():
    """Main landing page for retroNet"""
    return render_template('landing/landing.html')