from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.config import DevConfig

db = SQLAlchemy()
login_manager = LoginManager()

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
    # from app.models import Teacher, Student, Course, Grade
    with app.app_context():
        db.Model.metadata.reflect(db.engine)

    # Register Blueprints
    from app.main.routes import bp_main, bp_about
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_about)

    from app.auth.routes import bp_auth
    app.register_blueprint(bp_auth)

    from app.prof.routes import bp_prof
    app.register_blueprint(bp_prof)

    return app
