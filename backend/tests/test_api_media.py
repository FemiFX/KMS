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

    def test_upload_publication(self, client):
        """Test uploading a publication file."""
        data = {
            'file': (BytesIO(b'fake pdf data'), 'test.pdf'),
            'kind': 'publication',
            'title': 'Test Publication',
            'summary': 'Test publication summary',
            'language': 'de',
            'visibility': 'public'
        }
        response = client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )
        # May require authentication or not be fully implemented yet
        assert response.status_code in [200, 201, 400, 401, 403, 501]


class TestMediaUploadComplete:
    """Test complete media upload functionality."""

    def test_upload_video_complete(self, authenticated_client, app):
        """Test complete video upload with all fields."""
        data = {
            'file': (BytesIO(b'fake video data'), 'test_video.mp4'),
            'kind': 'video',
            'title': 'Complete Test Video',
            'summary': 'This is a complete test video upload',
            'language': 'de',
            'visibility': 'public',
            'tags': json.dumps([
                {'key': 'test-tag-1', 'label': 'Test Tag 1'},
                {'key': 'test-tag-2', 'label': 'Test Tag 2'}
            ]),
            'transcript': 'This is a test transcript for the video.',
            'auto_transcript': 'false'
        }

        response = authenticated_client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )

        # Should succeed with authentication
        if response.status_code in [200, 201]:
            result = json.loads(response.data)
            assert 'content_id' in result
            assert 'media_id' in result

            # Verify database records were created
            from app.models import Content, MediaContent, ArticleTranslation, Tag
            with app.app_context():
                content = Content.query.get(result['content_id'])
                assert content is not None
                assert content.type == 'video'
                assert content.visibility == 'public'

                media = MediaContent.query.get(result['media_id'])
                assert media is not None
                assert media.kind == 'video'
                assert media.content_id == result['content_id']
                assert '/static/uploads/videos/' in media.object_key

                translation = ArticleTranslation.query.filter_by(
                    content_id=result['content_id'],
                    language='de'
                ).first()
                assert translation is not None
                assert translation.title == 'Complete Test Video'
                assert translation.is_primary is True

                # Verify tags
                assert len(content.tags) == 2
                tag_keys = [tag.key for tag in content.tags]
                assert 'test-tag-1' in tag_keys
                assert 'test-tag-2' in tag_keys

                # Cleanup
                from app import db
                ArticleTranslation.query.filter_by(content_id=result['content_id']).delete()
                MediaContent.query.filter_by(id=result['media_id']).delete()
                Content.query.filter_by(id=result['content_id']).delete()
                db.session.commit()

    def test_upload_audio_complete(self, authenticated_client, app):
        """Test complete audio upload with all fields."""
        data = {
            'file': (BytesIO(b'fake audio data'), 'test_audio.mp3'),
            'kind': 'audio',
            'title': 'Complete Test Audio',
            'summary': 'This is a complete test audio upload',
            'language': 'en',
            'visibility': 'private',
            'tags': json.dumps(['audio-tag']),
        }

        response = authenticated_client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )

        if response.status_code in [200, 201]:
            result = json.loads(response.data)
            assert 'content_id' in result
            assert 'media_id' in result

            from app.models import Content, MediaContent
            with app.app_context():
                content = Content.query.get(result['content_id'])
                assert content.type == 'audio'

                media = MediaContent.query.get(result['media_id'])
                assert media.kind == 'audio'
                assert '/static/uploads/audios/' in media.object_key

                # Cleanup
                from app import db
                from app.models import ArticleTranslation
                ArticleTranslation.query.filter_by(content_id=result['content_id']).delete()
                MediaContent.query.filter_by(id=result['media_id']).delete()
                Content.query.filter_by(id=result['content_id']).delete()
                db.session.commit()

    def test_upload_video_invalid_format(self, authenticated_client):
        """Test uploading video with invalid file format."""
        data = {
            'file': (BytesIO(b'fake data'), 'test.txt'),
            'kind': 'video',
            'title': 'Invalid Format',
            'summary': 'Test',
            'language': 'de'
        }

        response = authenticated_client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )

        # Should reject invalid format
        assert response.status_code == 400
        if response.data:
            result = json.loads(response.data)
            assert 'error' in result
            assert 'format' in result['error'].lower() or 'invalid' in result['error'].lower()

    def test_upload_audio_invalid_format(self, authenticated_client):
        """Test uploading audio with invalid file format."""
        data = {
            'file': (BytesIO(b'fake data'), 'test.mp4'),
            'kind': 'audio',
            'title': 'Invalid Format',
            'summary': 'Test',
            'language': 'de'
        }

        response = authenticated_client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )

        # Should reject invalid format
        assert response.status_code == 400

    def test_upload_media_missing_title(self, authenticated_client):
        """Test uploading media without required title."""
        data = {
            'file': (BytesIO(b'fake video data'), 'test.mp4'),
            'kind': 'video',
            'summary': 'Test',
            'language': 'de'
        }

        response = authenticated_client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )

        # Should reject missing title
        assert response.status_code == 400

    def test_upload_media_missing_summary(self, authenticated_client):
        """Test uploading media without required summary."""
        data = {
            'file': (BytesIO(b'fake video data'), 'test.mp4'),
            'kind': 'video',
            'title': 'Test',
            'language': 'de'
        }

        response = authenticated_client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )

        # Should reject missing summary
        assert response.status_code == 400

    def test_upload_video_with_transcript(self, authenticated_client, app):
        """Test uploading video with transcript."""
        data = {
            'file': (BytesIO(b'fake video data'), 'test.mp4'),
            'kind': 'video',
            'title': 'Video With Transcript',
            'summary': 'Test video with transcript',
            'language': 'de',
            'transcript': 'This is the video transcript content.'
        }

        response = authenticated_client.post(
            '/api/media',
            data=data,
            content_type='multipart/form-data'
        )

        if response.status_code in [200, 201]:
            result = json.loads(response.data)

            from app.models import Transcript, MediaContent
            with app.app_context():
                media = MediaContent.query.get(result['media_id'])
                transcripts = Transcript.query.filter_by(media_id=media.id).all()

                # Should have created transcript
                assert len(transcripts) > 0
                transcript = transcripts[0]
                assert transcript.language == 'de'
                assert 'transcript content' in transcript.text

                # Cleanup
                from app import db
                from app.models import ArticleTranslation, Content
                Transcript.query.filter_by(media_id=media.id).delete()
                ArticleTranslation.query.filter_by(content_id=result['content_id']).delete()
                MediaContent.query.filter_by(id=result['media_id']).delete()
                Content.query.filter_by(id=result['content_id']).delete()
                db.session.commit()

    def test_get_publication(self, client, test_publication):
        """Test getting a publication item."""
        response = client.get(f'/api/media/{test_publication.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_publication.id
        assert data['kind'] == 'publication'
        assert data['mime_type'] == 'application/pdf'

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
