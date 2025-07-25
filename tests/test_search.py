import pytest
from src.app import create_app
from src.models import db


class TestSearchRoutes:
    @pytest.fixture
    def app(self):
        """Create application for testing"""
        app = create_app("testing")
        app.config["TESTING"] = True
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_search_suggestions_endpoint_exists(self, client):
        """Test that search suggestions endpoint is accessible"""
        response = client.get("/api/search/suggestions?query=test&language=en")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "data" in data
        assert "success" in data
        # Should return empty suggestions since no data in test DB
        assert data["data"]["suggestions"] == []

    def test_search_suggestions_empty_query(self, client):
        """Test search suggestions with empty query"""
        response = client.get("/api/search/suggestions?query=&language=en")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["suggestions"] == []

    def test_search_suggestions_with_language_param(self, client):
        """Test search suggestions with different language parameters"""
        # Test with Thai language
        response = client.get("/api/search/suggestions?query=test&language=th")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "data" in data
        assert data["data"]["suggestions"] == []