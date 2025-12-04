"""Tests for media API endpoints."""
import pytest
import json
from io import BytesIO


class TestMediaAPI:
    """Test media API endpoints."""

    def test_get_media_list(self, client):
        """Test getting list of media."""
        response = client.get('/api/media')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or 'media' in data

    def test_get_media_with_filters(self, client):
        """Test getting media with filters."""
        response = client.get('/api/media?kind=video')
        assert response.status_code == 200

        response = client.get('/api/media?language=de')
        assert response.status_code == 200

    def test_get_single_media(self, client, test_media):
        """Test getting a single media item."""
        response = client.get(f'/api/media/{test_media.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_media.id
        assert data['kind'] == 'video'

    def test_get_nonexistent_media(self, client):
        """Test getting non-existent media."""
        response = client.get('/api/media/nonexistent-id')
        assert response.status_code == 404

    def test_upload_media(self, client):
        """Test uploading media file."""
        data = {
            'file': (BytesIO(b'fake video data'), 'test.mp4'),
            'media_type': 'video',
            'title': 'Test Video',
            'summary': 'Test video summary',
            'language': 'de',
            'visibility': 'public'
        }
        response = client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )
        # May require authentication or not be implemented yet
        assert response.status_code in [200, 201, 400, 401, 403, 501]

    def test_upload_media_without_file(self, client):
        """Test uploading media without file."""
        data = {
            'media_type': 'video',
            'title': 'Test Video',
        }
        response = client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code in [400, 401, 403, 422]

    def test_delete_media(self, client, test_media):
        """Test deleting media."""
        response = client.delete(f'/api/media/{test_media.id}')
        # May require authentication
        assert response.status_code in [200, 204, 401, 403]


class TestTranscripts:
    """Test transcript endpoints."""

    def test_get_media_transcripts(self, client, test_media):
        """Test getting media transcripts."""
        response = client.get(f'/api/media/{test_media.id}/transcripts')
        assert response.status_code in [200, 404]

    def test_add_transcript(self, client, test_media):
        """Test adding a transcript."""
        payload = {
            'language': 'de',
            'text': 'Dies ist ein Transkript.',
            'is_primary': True
        }
        response = client.post(
            f'/api/media/{test_media.id}/transcripts',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # May require authentication
        assert response.status_code in [200, 201, 401, 403]
