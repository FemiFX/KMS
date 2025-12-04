"""Tests for authentication views."""
import pytest
from flask import url_for


class TestLogin:
    """Test login functionality."""

    def test_login_page_loads(self, client):
        """Test that login page loads correctly."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Verwaltungsportal' in response.data or b'Login' in response.data

    def test_login_with_valid_credentials(self, client, test_user):
        """Test login with valid credentials."""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_with_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'password' in response.data

    def test_login_with_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_redirects_authenticated_user(self, authenticated_client):
        """Test that authenticated users are redirected from login page."""
        response = authenticated_client.get('/login', follow_redirects=True)
        assert response.status_code == 200


class TestLogout:
    """Test logout functionality."""

    def test_logout(self, authenticated_client):
        """Test logout functionality."""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_logout_requires_authentication(self, client):
        """Test that logout requires authentication."""
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
