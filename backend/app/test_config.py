"""Test configuration."""
from datetime import timedelta


class TestConfig:
    """Testing configuration"""

    # Flask
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    DEBUG = False
    WTF_CSRF_ENABLED = False
    APP_MODE = 'full'
    PUBLIC_API_READ_ONLY = False

    # Session configuration
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # Database - use SQLite in memory
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}

    # Redis - not needed for tests
    REDIS_URL = 'redis://localhost:6379/0'

    # Celery - disable for tests
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'

    # MinIO/S3 - not needed for tests
    MINIO_ENDPOINT = 'localhost:9000'
    MINIO_ACCESS_KEY = 'minioadmin'
    MINIO_SECRET_KEY = 'minioadmin'
    MINIO_SECURE = False
    MINIO_BUCKET_NAME = 'test-bucket'

    # OpenAI
    OPENAI_API_KEY = 'test-key'

    # JWT
    JWT_SECRET_KEY = 'test-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3600)

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # File uploads
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi'}
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}

    # Embedding model
    EMBEDDING_MODEL = 'text-embedding-3-small'
    EMBEDDING_DIMENSIONS = 1536

    # Supported languages
    SUPPORTED_LANGUAGES = ['en', 'de', 'es', 'fr', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']
