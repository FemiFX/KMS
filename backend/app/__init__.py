from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from .config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
celery_app = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Configure Celery
    celery_app.conf.update(app.config)

    # Register API blueprints
    from app.api import content_bp, media_bp, tags_bp, search_bp, webhooks_bp

    app.register_blueprint(content_bp, url_prefix='/api/contents')
    app.register_blueprint(media_bp, url_prefix='/api/media')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')

    # Register views blueprint (HTML pages)
    from app.views import views_bp
    app.register_blueprint(views_bp)

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    return app
