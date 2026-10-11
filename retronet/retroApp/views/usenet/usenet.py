from flask import Blueprint, render_template

from retroApp.articles import build_categories

bp = Blueprint('usenet', __name__)

@bp.route('/usenet')
def usenet():
    """Newsreader index: group list on the left, nothing selected yet."""
    return render_template(
        'usenet/index.html',
        categories=build_categories(),
        threads=[],
        selected_group=None,
        selected_article=None,
    )