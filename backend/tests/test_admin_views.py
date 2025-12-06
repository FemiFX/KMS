"""Tests for admin views."""
import pytest


class TestAdminIndex:
    """Test admin dashboard."""

    def test_admin_index_requires_auth(self, client):
        """Test that admin index requires authentication."""
        response = client.get('/admin/')
        assert response.status_code == 302  # Redirect to login

    def test_admin_index_loads(self, authenticated_client):
        """Test that admin index loads for authenticated users."""
        response = authenticated_client.get('/admin/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Verwaltung' in response.data


class TestContentsPage:
    """Test contents listing page."""

    def test_contents_page_requires_auth(self, client):
        """Test that contents page requires authentication."""
        response = client.get('/admin/contents')
        assert response.status_code == 302

    def test_contents_page_loads(self, authenticated_client):
        """Test that contents page loads."""
        response = authenticated_client.get('/admin/contents')
        assert response.status_code == 200

    def test_contents_page_with_filters(self, authenticated_client):
        """Test contents page with filter parameters."""
        response = authenticated_client.get('/admin/contents?type=article')
        assert response.status_code == 200

        response = authenticated_client.get('/admin/contents?visibility=public')
        assert response.status_code == 200

        response = authenticated_client.get('/admin/contents?sort=newest')
        assert response.status_code == 200

    def test_contents_page_with_test_content(self, authenticated_client, test_content):
        """Test contents page displays test content."""
        response = authenticated_client.get('/admin/contents?lang=de')
        assert response.status_code == 200


class TestNewContentPage:
    """Test new content creation page."""

    def test_new_content_page_requires_auth(self, client):
        """Test that new content page requires authentication."""
        response = client.get('/admin/contents/new')
        assert response.status_code == 302

    def test_new_content_page_loads(self, authenticated_client):
        """Test that new content page loads."""
        response = authenticated_client.get('/admin/contents/new')
        assert response.status_code == 200
        assert b'Artikel' in response.data or b'Article' in response.data


class TestMediaPage:
    """Test media library page."""

    def test_media_page_requires_auth(self, client):
        """Test that media page requires authentication."""
        response = client.get('/admin/media')
        assert response.status_code == 302

    def test_media_page_loads(self, authenticated_client):
        """Test that media page loads."""
        response = authenticated_client.get('/admin/media')
        assert response.status_code == 200

    def test_media_page_with_filters(self, authenticated_client):
        """Test media page with filter parameters."""
        response = authenticated_client.get('/admin/media?type=video')
        assert response.status_code == 200

        response = authenticated_client.get('/admin/media?transcript=yes')
        assert response.status_code == 200

    def test_media_page_includes_content_id(self, authenticated_client, app, test_user):
        """Test that media page includes content_id in media data for building URLs."""
        from app.models import Content, MediaContent, ArticleTranslation
        from app import db

        with app.app_context():
            # Create video content with media
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
                title='Test Video for Media Library',
                markdown='Test',
                is_primary=True
            )
            translation.generate_slug()
            db.session.add(translation)
            db.session.commit()
            content_id = content.id

        response = authenticated_client.get('/admin/media?lang=de')
        assert response.status_code == 200

        # Check that the page contains content_id in a usable format for URL building
        # The template uses url_for('public.' + media.media_type + '_detail', content_id=media.content_id)
        # So the HTML should contain the content_id somewhere in the Details link
        assert str(content_id).encode() in response.data

        # Cleanup
        with app.app_context():
            MediaContent.query.filter_by(content_id=content_id).delete()
            ArticleTranslation.query.filter_by(content_id=content_id).delete()
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()

    def test_media_page_details_link_works(self, authenticated_client, app, test_user):
        """Test that the Details button links to the correct type-specific route."""
        from app.models import Content, MediaContent, ArticleTranslation
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
                title='Test Audio for Link',
                markdown='Test',
                is_primary=True
            )
            translation.generate_slug()
            db.session.add(translation)
            db.session.commit()
            content_id = content.id

        response = authenticated_client.get('/admin/media?type=audio&lang=de')
        assert response.status_code == 200

        # Check that the page contains a link to the audio detail page
        # The link should be: /contents/audio/{content_id}?lang=de
        expected_link = f'/contents/audio/{content_id}'
        assert expected_link.encode() in response.data

        # Cleanup
        with app.app_context():
            MediaContent.query.filter_by(content_id=content_id).delete()
            ArticleTranslation.query.filter_by(content_id=content_id).delete()
            Content.query.filter_by(id=content_id).delete()
            db.session.commit()


class TestMediaUploadPage:
    """Test media upload page."""

    def test_media_upload_page_requires_auth(self, client):
        """Test that media upload page requires authentication."""
        response = client.get('/admin/media/upload')
        assert response.status_code == 302

    def test_media_upload_page_loads(self, authenticated_client):
        """Test that media upload page loads."""
        response = authenticated_client.get('/admin/media/upload')
        assert response.status_code == 200
        assert b'upload' in response.data.lower() or b'hochladen' in response.data.lower()


class TestSearchPage:
    """Test search page."""

    def test_search_page_requires_auth(self, client):
        """Test that search page requires authentication."""
        response = client.get('/admin/search')
        assert response.status_code == 302

    def test_search_page_loads(self, authenticated_client):
        """Test that search page loads."""
        response = authenticated_client.get('/admin/search')
        assert response.status_code == 200

    def test_search_with_query(self, authenticated_client, test_content):
        """Test search with query parameter."""
        response = authenticated_client.get('/admin/search?q=test&lang=de')
        assert response.status_code == 200

    def test_search_with_filters(self, authenticated_client):
        """Test search with filter parameters."""
        response = authenticated_client.get('/admin/search?q=test&type=article&lang=de')
        assert response.status_code == 200


class TestTagsPage:
    """Test tags management page."""

    def test_tags_page_requires_auth(self, client):
        """Test that tags page requires authentication."""
        response = client.get('/admin/tags')
        assert response.status_code == 302

    def test_tags_page_loads(self, authenticated_client):
        """Test that tags page loads."""
        response = authenticated_client.get('/admin/tags')
        assert response.status_code == 200

    def test_tags_page_with_namespace_filter(self, authenticated_client):
        """Test tags page with namespace filter."""
        response = authenticated_client.get('/admin/tags?namespace=general')
        assert response.status_code == 200


class TestTranslationsPage:
    """Test translations management page."""

    def test_translations_page_requires_auth(self, client):
        """Test that translations page requires authentication."""
        response = client.get('/admin/translations')
        assert response.status_code == 302

    def test_translations_page_loads(self, authenticated_client):
        """Test that translations page loads."""
        response = authenticated_client.get('/admin/translations')
        assert response.status_code == 200

    def test_translations_page_with_filters(self, authenticated_client):
        """Test translations page with filter parameters."""
        response = authenticated_client.get('/admin/translations?type=article')
        assert response.status_code == 200

        response = authenticated_client.get('/admin/translations?incomplete=true')
        assert response.status_code == 200
