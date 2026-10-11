import os

from flask import Flask
from asgiref.wsgi import WsgiToAsgi

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
    # schema.sql is written entirely with CREATE ... IF NOT EXISTS, so running
    # it on every boot is idempotent: it creates anything missing and leaves
    # existing tables (and their data) alone.
    with app.app_context():
        db.init_db()

    from .template_filters import register_filters
    register_filters(app)

    from .middleware import visitors
    visitors(app)

    from .articles import article_tools
    article_tools(app)

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

    from .views.usenet import usenet
    app.register_blueprint(usenet.bp)
    
    return app

def create_asgi_app():
    flask_app = create_retroNet()
    return WsgiToAsgi(flask_app)