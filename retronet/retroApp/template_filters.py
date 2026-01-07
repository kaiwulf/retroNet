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

    @app.template_filter('format_message')
    def format_message(text):
        """Format message body with proper styling for quotes and signatures"""
        if not text:
            return ''

        lines = text.split('\n')
        formatted_lines = []
        in_signature = False

        for line in lines:
            # Check for signature delimiter
            if line.strip() == '--':
                in_signature = True
                formatted_lines.append('<div class="signature">')
                formatted_lines.append(escape(line))
                continue
            
            if in_signature:
                formatted_lines.append(escape(line))
                continue
            
            # Count quote depth
            quote_depth = 0
            stripped = line
            while stripped.startswith('>'):
                quote_depth += 1
                stripped = stripped[1:].lstrip()
            
            if quote_depth > 0:
                css_class = f'quoted-line quoted-line-{min(quote_depth, 3)}'
                formatted_lines.append(f'<span class="{css_class}">{escape(line)}</span>')
            else:
                formatted_lines.append(escape(line))

        if in_signature:
            formatted_lines.append('</div>')

        return Markup('\n'.join(formatted_lines))