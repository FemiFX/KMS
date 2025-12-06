"""Pytest configuration and fixtures for testing."""
import os
import pytest
from app import create_app, db
from app.test_config import TestConfig
from app.models import User, Content, ArticleTranslation, MediaContent, Tag
from datetime import datetime


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Set testing environment variables
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    # Create app with test config
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a new database session for a test."""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()
        db.session.remove()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            email='test@example.com',
            is_active=True
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    return client


@pytest.fixture
def test_content(app, test_user):
    """Create test content with translation."""
    with app.app_context():
        content = Content(
            type='article',
            created_by_id=test_user.id,
            visibility='public'
        )
        db.session.add(content)
        db.session.flush()

        translation = ArticleTranslation(
            content_id=content.id,
            language='de',
            title='Test Artikel',
            markdown='# Test Inhalt\n\nDies ist ein Test.',
            is_primary=True
        )
        translation.generate_slug()  # Generate slug before saving
        db.session.add(translation)
        db.session.commit()

        yield content

        # Cleanup
        ArticleTranslation.query.filter_by(content_id=content.id).delete()
        db.session.delete(content)
        db.session.commit()


@pytest.fixture
def test_tag(app):
    """Create a test tag."""
    with app.app_context():
        tag = Tag(
            key='test-tag',
            default_label='Test Tag',
            namespace='general',
            color='#FF0000'
        )
        db.session.add(tag)
        db.session.commit()
        yield tag
        db.session.delete(tag)
        db.session.commit()


@pytest.fixture
def test_media(app, test_user):
    """Create test media content."""
    with app.app_context():
        content = Content(
            type='video',
            created_by_id=test_user.id,
            visibility='public'
        )
        db.session.add(content)
        db.session.flush()

        media = MediaContent(
            content_id=content.id,
            kind='video',
            object_key='test/video.mp4',
            mime_type='video/mp4',
            file_size=1024000,
            duration_seconds=120.5,
            original_language='de'
        )
        db.session.add(media)
        db.session.commit()

        yield media

        # Cleanup
        db.session.delete(media)
        db.session.delete(content)
        db.session.commit()


@pytest.fixture
def test_publication(app, test_user):
    """Create test publication content."""
    with app.app_context():
        content = Content(
            type='publication',
            created_by_id=test_user.id,
            visibility='public'
        )
        db.session.add(content)
        db.session.flush()

        publication = MediaContent(
            content_id=content.id,
            kind='publication',
            object_key='test/document.pdf',
            mime_type='application/pdf',
            file_size=512000,
            original_language='de'
        )
        db.session.add(publication)

        translation = ArticleTranslation(
            content_id=content.id,
            language='de',
            title='Test Publication',
            markdown='Test publication content',
            is_primary=True
        )
        translation.generate_slug()
        db.session.add(translation)
        db.session.commit()

        yield publication

        # Cleanup
        ArticleTranslation.query.filter_by(content_id=content.id).delete()
        db.session.delete(publication)
        db.session.delete(content)
        db.session.commit()


@pytest.fixture
def test_video(app, test_user):
    """Create test video content."""
    with app.app_context():
        content = Content(
            type='video',
            created_by_id=test_user.id,
            visibility='public'
        )
        db.session.add(content)
        db.session.flush()

        video = MediaContent(
            content_id=content.id,
            kind='video',
            object_key='/static/uploads/videos/test.mp4',
            mime_type='video/mp4',
            file_size=2048000,
            duration_seconds=180.5,
            original_language='de'
        )
        db.session.add(video)

        translation = ArticleTranslation(
            content_id=content.id,
            language='de',
            title='Test Video',
            markdown='Test video description',
            is_primary=True
        )
        translation.generate_slug()
        db.session.add(translation)
        db.session.commit()

        yield video

        # Cleanup
        ArticleTranslation.query.filter_by(content_id=content.id).delete()
        db.session.delete(video)
        db.session.delete(content)
        db.session.commit()


@pytest.fixture
def test_audio(app, test_user):
    """Create test audio content."""
    with app.app_context():
        content = Content(
            type='audio',
            created_by_id=test_user.id,
            visibility='public'
        )
        db.session.add(content)
        db.session.flush()

        audio = MediaContent(
            content_id=content.id,
            kind='audio',
            object_key='/static/uploads/audios/test.mp3',
            mime_type='audio/mpeg',
            file_size=768000,
            duration_seconds=240.0,
            original_language='de'
        )
        db.session.add(audio)

        translation = ArticleTranslation(
            content_id=content.id,
            language='de',
            title='Test Audio',
            markdown='Test audio description',
            is_primary=True
        )
        translation.generate_slug()
        db.session.add(translation)
        db.session.commit()

        yield audio

        # Cleanup
        ArticleTranslation.query.filter_by(content_id=content.id).delete()
        db.session.delete(audio)
        db.session.delete(content)
        db.session.commit()
