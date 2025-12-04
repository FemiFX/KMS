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
        assert response.status_code == 200
        assert b'Test Artikel' in response.data

    def test_content_detail_with_language(self, client, test_content):
        """Test content detail with language parameter."""
        response = client.get(f'/contents/{test_content.id}?lang=de')
        assert response.status_code == 200

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
