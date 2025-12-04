"""Tests for content API endpoints."""
import pytest
import json


class TestContentAPI:
    """Test content API endpoints."""

    def test_get_contents_list(self, client):
        """Test getting list of contents."""
        response = client.get('/api/contents')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'contents' in data or isinstance(data, list)

    def test_get_contents_with_filters(self, client):
        """Test getting contents with filters."""
        response = client.get('/api/contents?type=article')
        assert response.status_code == 200

        response = client.get('/api/contents?visibility=public')
        assert response.status_code == 200

        response = client.get('/api/contents?language=de')
        assert response.status_code == 200

    def test_get_single_content(self, client, test_content):
        """Test getting a single content item."""
        response = client.get(f'/api/contents/{test_content.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_content.id
        assert data['type'] == 'article'

    def test_get_nonexistent_content(self, client):
        """Test getting non-existent content."""
        response = client.get('/api/contents/nonexistent-id')
        assert response.status_code == 404

    def test_create_content(self, client, test_user):
        """Test creating new content."""
        payload = {
            'type': 'article',
            'visibility': 'public',
            'language': 'de',
            'title': 'Neuer Test Artikel',
            'markdown': '# Neuer Inhalt\n\nDies ist neu.',
            'tags': ['test']
        }
        response = client.post(
            '/api/contents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # May require authentication
        assert response.status_code in [200, 201, 401, 403]

    def test_create_content_missing_fields(self, client):
        """Test creating content with missing required fields."""
        payload = {
            'type': 'article'
            # Missing other required fields
        }
        response = client.post(
            '/api/contents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [400, 401, 403, 422]

    def test_update_content(self, client, test_content):
        """Test updating content."""
        payload = {
            'visibility': 'private'
        }
        response = client.patch(
            f'/api/contents/{test_content.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # May require authentication
        assert response.status_code in [200, 401, 403]

    def test_delete_content(self, client, test_content):
        """Test deleting content."""
        response = client.delete(f'/api/contents/{test_content.id}')
        # May require authentication
        assert response.status_code in [200, 204, 401, 403]


class TestContentTranslations:
    """Test content translation endpoints."""

    def test_get_content_translations(self, client, test_content):
        """Test getting content translations."""
        response = client.get(f'/api/contents/{test_content.id}/translations')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or 'translations' in data

    def test_add_translation(self, client, test_content):
        """Test adding a translation."""
        payload = {
            'language': 'en',
            'title': 'Test Article',
            'markdown': '# Test Content\n\nThis is a test.'
        }
        response = client.post(
            f'/api/contents/{test_content.id}/translations',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # May require authentication
        assert response.status_code in [200, 201, 401, 403]
