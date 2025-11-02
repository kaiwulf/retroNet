from flask import Flask, jsonify, request
from asgiref.wsgi import WsgiToAsgi
import asyncio, httpx
import aiosqlite
import os
from datetime import datetime
from functools import wraps

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

    from .views import landing
    app.register_blueprint(landing.bp)
    # app.add_url_rule('/', endpoint='index')

    from .models import db
    from .views.auth import auth
    db.init_app(app)
    app.register_blueprint(auth.bp)

    # from .views.auth import signin
    # app.register_blueprint(signin.bp)
    # app.add_url_rule('/signin', endpoint='index')

    # from .views.auth import signup
    # app.register_blueprint(signup.bp)
    # app.add_url_rule('/signup', endpoint='index')

    from .views import user
    app.register_blueprint(user.bp)
    # app.add_url_rule('/user')

    # from .views import home
    # app.register_blueprint(home.bp)
    # app.add_url_rule('/home')

    from .views import chat
    app.register_blueprint(chat.bp)
    # app.add_url_rule('/chat')

    from .views import usenet
    app.register_blueprint(usenet.bp)
    # app.add_url_rule('/usenet')
    
    return app

def create_asgi_app():
    flask_app = create_retroNet()
    return WsgiToAsgi(flask_app)