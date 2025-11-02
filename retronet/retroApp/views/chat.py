from flask import Blueprint, render_template

bp = Blueprint('chat', __name__)

@bp.route('/chat', methods=('GET', 'POST'))
def chat():
    """Chat page for retroNet"""
    return render_template('chat/chat.html')