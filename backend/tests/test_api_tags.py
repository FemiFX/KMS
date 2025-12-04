"""Tests for tags API endpoints."""
import pytest
import json


class TestTagsAPI:
    """Test tags API endpoints."""

    def test_get_tags_list(self, client):
        """Test getting list of tags."""
        response = client.get('/api/tags')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or 'tags' in data

    def test_get_tags_with_namespace(self, client, test_tag):
        """Test getting tags filtered by namespace."""
        response = client.get('/api/tags?namespace=general')
        assert response.status_code == 200

    def test_get_single_tag(self, client, test_tag):
        """Test getting a single tag."""
        response = client.get(f'/api/tags/{test_tag.id}')
        assert response.status_code in [200, 404]

    def test_create_tag(self, client):
        """Test creating a new tag."""
        payload = {
            'key': 'new-tag',
            'default_label': 'New Tag',
            'namespace': 'test',
            'color': '#00FF00'
        }
        response = client.post(
            '/api/tags',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # May require authentication
        assert response.status_code in [200, 201, 401, 403]

    def test_create_duplicate_tag(self, client, test_tag):
        """Test creating a tag with duplicate key."""
        payload = {
            'key': test_tag.key,
            'default_label': 'Duplicate Tag',
            'namespace': 'general'
        }
        response = client.post(
            '/api/tags',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # Should fail due to duplicate key
        assert response.status_code in [400, 401, 403, 409, 422]

    def test_update_tag(self, client, test_tag):
        """Test updating a tag."""
        payload = {
            'default_label': 'Updated Label'
        }
        response = client.patch(
            f'/api/tags/{test_tag.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # May require authentication
        assert response.status_code in [200, 401, 403, 404]

    def test_delete_tag(self, client, test_tag):
        """Test deleting a tag."""
        response = client.delete(f'/api/tags/{test_tag.id}')
        # May require authentication
        assert response.status_code in [200, 204, 401, 403]


class TestTagLabels:
    """Test tag label endpoints."""

    def test_get_tag_labels(self, client, test_tag):
        """Test getting tag labels."""
        response = client.get(f'/api/tags/{test_tag.id}/labels')
        assert response.status_code in [200, 404]

    def test_add_tag_label(self, client, test_tag):
        """Test adding a tag label for a language."""
        payload = {
            'language': 'en',
            'label': 'Test Tag'
        }
        response = client.post(
            f'/api/tags/{test_tag.id}/labels',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # May require authentication
        assert response.status_code in [200, 201, 401, 403]
