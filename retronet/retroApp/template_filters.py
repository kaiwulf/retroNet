from datetime import datetime

def register_filters(app):
    @app.template_filter('date_format')
    def date_format(value):
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