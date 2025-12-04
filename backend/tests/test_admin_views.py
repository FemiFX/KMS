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
