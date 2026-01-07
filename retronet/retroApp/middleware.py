import hashlib
from datetime import datetime

def visitors(app):
    @app.before_request
    def track_visitor():
        """Track visitors on each page request"""
        from flask import request, session, g
        from retroApp.models.db import get_db

        # Skip tracking for static files and stats stream
        if request.endpoint in ('static', 'landing.stats_stream'):
            return

        # Get or create visitor ID from session
        if 'visitor_id' not in session:
            # Create unique visitor ID based on IP and user agent
            visitor_id = hashlib.md5(
                f"{request.remote_addr}{request.headers.get('User-Agent', '')}".encode()
            ).hexdigest()
            session['visitor_id'] = visitor_id
            session.permanent = True  # Keep session alive
            
            # Record new visitor
            try:
                db = get_db()
                db.execute(
                    "INSERT OR IGNORE INTO visitors (visitor_id, first_seen, last_seen) VALUES (?, ?, ?)",
                    (visitor_id, datetime.now(), datetime.now())
                )
                db.commit()
            except Exception as e:
                # Table might not exist yet, ignore error
                print(f"Visitor tracking error: {e}")
                pass
        else:
            # Update last seen for existing visitor
            try:
                db = get_db()
                db.execute(
                    "UPDATE visitors SET last_seen = ? WHERE visitor_id = ?",
                    (datetime.now(), session['visitor_id'])
                )
                db.commit()
            except Exception as e:
                # Ignore errors
                pass

        # Update last_seen for logged-in users
        if hasattr(g, 'user') and g.user:
            try:
                db = get_db()
                db.execute(
                    "UPDATE user SET last_seen = ? WHERE id = ?",
                    (datetime.now(), g.user['id'])
                )
                db.commit()
            except:
                pass