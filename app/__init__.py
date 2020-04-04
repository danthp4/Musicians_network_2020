from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads

from app.config import DevConfig

db = SQLAlchemy()
images = UploadSet('images', IMAGES)
login_manager = LoginManager()


def page_not_found(e):
    return render_template('404.html'), 404


def internal_server_error(e):
    return render_template('500.html'), 500


def create_app(config_class=DevConfig):
    """
    Creates an application instance to run using settings from config.py
    :return: A Flask object
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    login_manager.init_app(app)

    # Initialise the database and create tables
    db.init_app(app)
    configure_uploads(app, images)
    from app.models import Profile, Musician, Venue, Media, \
        Administrator, Genre, Profile_Genre
    with app.app_context():
        db.create_all()

    # Register error handlers
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    # Register Blueprints
    from app.main.routes import bp_main
    app.register_blueprint(bp_main)

    from app.abt.routes import bp_about
    app.register_blueprint(bp_about)

    from app.auth.routes import bp_auth
    app.register_blueprint(bp_auth)

    from app.prof.routes import bp_prof
    app.register_blueprint(bp_prof)

    return app
