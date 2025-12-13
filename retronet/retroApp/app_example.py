"""
Example Flask app setup with custom Jinja2 filters
This shows how to integrate the template filters into your Flask application
"""

from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# METHOD 1: Using decorators (inline in your main Flask file)
@app.template_filter('date_format')
def date_format(value):
    """Format a date to 'January 15, 2024'"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except (ValueError, AttributeError):
            return value
    if isinstance(value, datetime):
        return value.strftime("%B %d, %Y")
    return str(value)


@app.template_filter('datetime_format')
def datetime_format(value):
    """Format a datetime to 'January 15, 2024 at 3:45 PM'"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except (ValueError, AttributeError):
            return value
    if isinstance(value, datetime):
        return value.strftime("%B %d, %Y at %I:%M %p")
    return str(value)


# METHOD 2: Import from separate file (if using template_filters.py)
# from template_filters import register_filters
# register_filters(app)


# Example route
@app.route('/profile/<username>')
def profile(username):
    # Example user data structure
    user = {
        'username': username,
        'profile_pic': '/static/images/default-avatar.png',
        'about_me': 'Just a cool retroNet user!',
        'status': 'Online',
        'location': 'Cyberspace',
        'age': 25,
        'website': 'https://example.com',
        'created_at': datetime(2024, 1, 15, 14, 30),  # DateTime object
        'stalker_count': 8,
        'stalker_list': [],
        'recent_blog_posts': [],
        'feed_items': [],
        'comments': [],
        'comment_count': 0,
    }
    
    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
