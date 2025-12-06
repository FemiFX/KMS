"""Tests for public views."""
import pytest


class TestPublicHome:
    """Test public homepage."""

    def test_homepage_loads(self, client):
        """Test that homepage loads correctly."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'UN-Dekade' in response.data or b'UN Decade' in response.data

    def test_homepage_has_search(self, client):
        """Test that homepage has search functionality."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'search' in response.data.lower() or b'suchen' in response.data.lower()

    def test_homepage_language_param(self, client):
        """Test homepage with language parameter."""
        response = client.get('/?lang=en')
        assert response.status_code == 200

        response = client.get('/?lang=de')
        assert response.status_code == 200

        response = client.get('/?lang=fr')
        assert response.status_code == 200


class TestContentDetail:
    """Test content detail view."""

    def test_content_detail_loads(self, client, test_content):
        """Test that content detail page loads."""
        response = client.get(f'/contents/{test_content.id}')
        assert response.status_code in [200, 302]  # May redirect to type-specific route

    def test_content_detail_with_language(self, client, test_content):
        """Test content detail with language parameter."""
        response = client.get(f'/contents/{test_content.id}?lang=de')
        assert response.status_code in [200, 302]  # May redirect to type-specific route

    def test_content_detail_not_found(self, client):
        """Test content detail with non-existent ID."""
        response = client.get('/contents/nonexistent-id')
        assert response.status_code == 404

    def test_content_detail_without_translation(self, client, app, test_user):
        """Test content detail without translations."""
        from app.models import Content
        from app import db

        with app.app_context():
            content = Content(
                type='article',
                created_by_id=test_user.id,
                visibility='public'
            )
            db.session.add(content)
            db.session.commit()
            content_id = content.id

        response = client.get(f'/contents/{content_id}')
        assert response.status_code == 404

        # Cleanup
        with app.app_context():
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()


class TestArticleDetail:
    """Test article-specific detail view."""

    def test_article_detail_loads(self, client, test_content):
        """Test that article detail page loads correctly."""
        response = client.get(f'/contents/article/{test_content.id}')
        assert response.status_code == 200
        assert b'Test Artikel' in response.data

    def test_article_detail_with_language(self, client, test_content):
        """Test article detail with language parameter."""
        response = client.get(f'/contents/article/{test_content.id}?lang=de')
        assert response.status_code == 200

    def test_article_detail_wrong_type_redirects(self, client, app, test_user):
        """Test accessing article route with non-article content redirects."""
        from app.models import Content, ArticleTranslation
        from app import db

        with app.app_context():
            # Create video content
            content = Content(
                type='video',
                created_by_id=test_user.id,
                visibility='public'
            )
            db.session.add(content)
            db.session.flush()

            translation = ArticleTranslation(
                content_id=content.id,
                language='de',
                title='Test Video',
                markdown='Test',
                is_primary=True
            )
            translation.generate_slug()  # Generate slug before saving
            db.session.add(translation)
            db.session.commit()
            content_id = content.id

        # Try to access as article - should redirect to video
        response = client.get(f'/contents/article/{content_id}')
        assert response.status_code == 302  # Redirect to correct type

        # Cleanup
        with app.app_context():
            ArticleTranslation.query.filter_by(content_id=content_id).delete()
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()


class TestVideoDetail:
    """Test video-specific detail view."""

    def test_video_detail_loads(self, client, app, test_user):
        """Test that video detail page loads correctly."""
        from app.models import Content, ArticleTranslation, MediaContent
        from app import db

        with app.app_context():
            # Create video content
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
                object_key='/static/uploads/videos/test.mp4',
                mime_type='video/mp4',
                file_size=1024000,
                original_language='de'
            )
            db.session.add(media)

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
            content_id = content.id

        response = client.get(f'/contents/video/{content_id}')
        assert response.status_code == 200
        assert b'Test Video' in response.data
        assert b'video' in response.data.lower()

        # Cleanup
        with app.app_context():
            MediaContent.query.filter_by(content_id=content_id).delete()
            ArticleTranslation.query.filter_by(content_id=content_id).delete()
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()

    def test_video_detail_with_language(self, client, app, test_user):
        """Test video detail with language parameter."""
        from app.models import Content, ArticleTranslation, MediaContent
        from app import db

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
                object_key='/static/uploads/videos/test.mp4',
                mime_type='video/mp4',
                file_size=1024000,
                original_language='de'
            )
            db.session.add(media)

            translation = ArticleTranslation(
                content_id=content.id,
                language='de',
                title='Test Video DE',
                markdown='Test',
                is_primary=True
            )
            translation.generate_slug()
            db.session.add(translation)
            db.session.commit()
            content_id = content.id

        response = client.get(f'/contents/video/{content_id}?lang=de')
        assert response.status_code == 200

        # Cleanup
        with app.app_context():
            MediaContent.query.filter_by(content_id=content_id).delete()
            ArticleTranslation.query.filter_by(content_id=content_id).delete()
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()


class TestAudioDetail:
    """Test audio-specific detail view."""

    def test_audio_detail_loads(self, client, app, test_user):
        """Test that audio detail page loads correctly."""
        from app.models import Content, ArticleTranslation, MediaContent
        from app import db

        with app.app_context():
            # Create audio content
            content = Content(
                type='audio',
                created_by_id=test_user.id,
                visibility='public'
            )
            db.session.add(content)
            db.session.flush()

            media = MediaContent(
                content_id=content.id,
                kind='audio',
                object_key='/static/uploads/audios/test.mp3',
                mime_type='audio/mpeg',
                file_size=512000,
                original_language='de'
            )
            db.session.add(media)

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
            content_id = content.id

        response = client.get(f'/contents/audio/{content_id}')
        assert response.status_code == 200
        assert b'Test Audio' in response.data
        assert b'audio' in response.data.lower() or b'Audio' in response.data

        # Cleanup
        with app.app_context():
            MediaContent.query.filter_by(content_id=content_id).delete()
            ArticleTranslation.query.filter_by(content_id=content_id).delete()
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()


class TestPublicationDetail:
    """Test publication-specific detail view."""

    def test_publication_detail_loads(self, client, app, test_user):
        """Test that publication detail page loads correctly."""
        from app.models import Content, ArticleTranslation, MediaContent
        from app import db

        with app.app_context():
            # Create publication content
            content = Content(
                type='publication',
                created_by_id=test_user.id,
                visibility='public'
            )
            db.session.add(content)
            db.session.flush()

            media = MediaContent(
                content_id=content.id,
                kind='publication',
                object_key='/static/uploads/publications/test.pdf',
                mime_type='application/pdf',
                file_size=256000,
                original_language='de'
            )
            db.session.add(media)

            translation = ArticleTranslation(
                content_id=content.id,
                language='de',
                title='Test Publication',
                markdown='Test publication description',
                is_primary=True
            )
            translation.generate_slug()
            db.session.add(translation)
            db.session.commit()
            content_id = content.id

        response = client.get(f'/contents/publication/{content_id}')
        assert response.status_code == 200
        assert b'Test Publication' in response.data

        # Cleanup
        with app.app_context():
            MediaContent.query.filter_by(content_id=content_id).delete()
            ArticleTranslation.query.filter_by(content_id=content_id).delete()
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()
