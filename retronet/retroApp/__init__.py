from flask import Flask, jsonify, request
from asgiref.wsgi import WsgiToAsgi
import asyncio, httpx
import aiosqlite
import os
from datetime import datetime
from functools import wraps
import hashlib

# def ycms_factory(test_config=None):
def create_retroNet(test_config=None):
    app = Flask(__name__,
        static_folder='static',
        instance_relative_config=True
    )
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'retroNet.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .models import db
    db.init_app(app)
    with app.app_context():
        try:
            db.init_db()
            print("✅ Database initialized!")
        except Exception as e:
            print(f"ℹ️  Database already exists or error: {e}")

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


    from .views import landing
    app.register_blueprint(landing.bp)

    from .views.auth import auth
    app.register_blueprint(auth.bp)

    from .views.user import user
    app.register_blueprint(user.bp)
    
    from .views.user import create
    app.register_blueprint(create.bp)

    from .views import chat
    app.register_blueprint(chat.bp)

    from .views import usenet
    app.register_blueprint(usenet.bp)
    
    return app

def create_asgi_app():
    flask_app = create_retroNet()
    return WsgiToAsgi(flask_app)