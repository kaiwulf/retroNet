"""
Custom Jinja2 template filters for retroNet Flask app
Add these to your Flask application to fix the date_format and datetime_format errors
"""

from datetime import datetime


def date_format(value):
    """
    Format a date object or datetime object to a simple date string
    Example: "January 15, 2024"
    """
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


def datetime_format(value):
    """
    Format a datetime object to include time
    Example: "January 15, 2024 at 3:45 PM"
    """
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


def register_filters(app):
    """
    Register all custom filters with the Flask app
    
    Usage in your Flask app:
        from template_filters import register_filters
        
        app = Flask(__name__)
        register_filters(app)
    """
    app.jinja_env.filters['date_format'] = date_format
    app.jinja_env.filters['datetime_format'] = datetime_format


# Alternative: Use decorators in your main Flask file
# 
# @app.template_filter('date_format')
# def date_format(value):
#     # ... filter code here ...
#     pass
