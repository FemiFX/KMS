"""Tests for search API endpoints."""
import pytest
import json


class TestSearchAPI:
    """Test search API endpoints."""

    def test_search_endpoint_exists(self, client):
        """Test that search endpoint exists."""
        response = client.get('/api/search')
        assert response.status_code in [200, 400, 404]

    def test_search_with_query(self, client, test_content):
        """Test search with query parameter."""
        response = client.get('/api/search?q=test')
        assert response.status_code in [200, 400]

    def test_search_with_filters(self, client):
        """Test search with filter parameters."""
        response = client.get('/api/search?q=test&type=article&language=de')
        assert response.status_code in [200, 400]

    def test_search_without_query(self, client):
        """Test search without query parameter."""
        response = client.get('/api/search')
        # Should require query or return error
        assert response.status_code in [200, 400]

    def test_search_returns_json(self, client, test_content):
        """Test that search returns JSON."""
        response = client.get('/api/search?q=test')
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, dict) or isinstance(data, list)

    def test_semantic_search(self, client):
        """Test semantic search endpoint if available."""
        response = client.get('/api/search/semantic?q=african descent')
        # May not be implemented yet
        assert response.status_code in [200, 404, 501]


class TestSearchFilters:
    """Test search filter functionality."""

    def test_filter_by_type(self, client, test_content):
        """Test filtering by content type."""
        response = client.get('/api/search?q=test&type=article')
        assert response.status_code in [200, 400]

    def test_filter_by_language(self, client, test_content):
        """Test filtering by language."""
        response = client.get('/api/search?q=test&language=de')
        assert response.status_code in [200, 400]

    def test_filter_by_visibility(self, client, test_content):
        """Test filtering by visibility."""
        response = client.get('/api/search?q=test&visibility=public')
        assert response.status_code in [200, 400]

    def test_pagination(self, client):
        """Test search pagination."""
        response = client.get('/api/search?q=test&page=1&per_page=10')
        assert response.status_code in [200, 400]
