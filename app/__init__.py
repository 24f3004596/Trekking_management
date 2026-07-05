from flask import Flask
from config import Config
from app.extensions import db, bcrypt, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints (to be done in later milestones)
    # from app.routes.main import main_bp
    # app.register_blueprint(main_bp)

    return app
