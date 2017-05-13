# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_uploads import UploadSet, DOCUMENTS, DATA, configure_uploads

# local imports
from config import app_config
from .models import User

# db variable initialization
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    # Code for login manager
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"

    # Code for db migrations
    migrate = Migrate(app, db)

    # Bootstrap
    Bootstrap(app)

    # Debugger
    DebugToolbarExtension(app)

    # # Configure the data uploading via Flask-Uploads
    # data_set = UploadSet('data_set', DOCUMENTS, DATA)
    # configure_uploads(app, data_set)

    from app import models

    # Register Blueprints
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    return app
