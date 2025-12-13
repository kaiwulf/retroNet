from flask import Blueprint, g, render_template
from retroApp.models.user.user import get_user_profile
import pprint

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/<username>')
def profile(username):
    """User profile page
    
    Shows user's profile including:
    - Profile info
    - Blog posts
    - Stalker count
    - Profile music
    """
    # Get user profile data from model
    print(f"In user profile")
    profile_data = get_user_profile(username)
    
    if profile_data is None:
        abort(404, f"User '{username}' not found")
    
    # Check if viewing own profile
    is_own_profile = False
    if g.user and g.user['username'] == username:
        is_own_profile = True

    print("profile data is...")
    pprint.pprint(profile_data)
    
    return render_template(
        'user/profile.html',
        user=profile_data,
        is_own_profile=is_own_profile
    )