import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize database
db = SQLAlchemy()


def create_app():
    """Creates and configures the Flask application."""
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MIDAS_ClaudiaLlop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger = logging.getLogger(__name__)
    logger.info("Configuring database connection...")

    db.init_app(app)
    logger.info("Initializing database...")

    from app.endpoints import routes
    app.register_blueprint(routes)

    return app
