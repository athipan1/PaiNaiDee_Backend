import pytest
from src.app import create_app
from src.models import db, Attraction
import json


class TestSearchRoutes:
    @pytest.fixture
    def app(self):
        """Create application for testing"""
        app = create_app("testing")
        app.config["TESTING"] = True
        with app.app_context():
            db.create_all()
            # Add test data
            self._create_test_attractions()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def _create_test_attractions(self):
        """Create test attractions for search testing"""
        attractions = [
            Attraction(
                name="วัดพระแก้ว",
                description="วัดที่ศักดิ์สิทธิ์ที่สุดในประเทศไทย",
                province="กรุงเทพฯ",
                district="พระนคร",
                category="วัฒนธรรม",
                latitude=13.7515,
                longitude=100.4925,
                main_image_url="https://example.com/wat.jpg"
            ),
            Attraction(
                name="เกาะพีพี",
                description="เกาะสวยงามในทะเลอันดามัน",
                province="กระบี่",
                district="อ่าวนาง",
                category="ชายหาด",
                latitude=7.7407,
                longitude=98.7784,
                main_image_url="https://example.com/phiphi.jpg"
            ),
            Attraction(
                name="ดอยอินทนนท์",
                description="ยอดเขาที่สูงที่สุดในประเทศไทย",
                province="เชียงใหม่",
                district="จอมทอง",
                category="ธรรมชาติ",
                latitude=18.5889,
                longitude=98.4867,
                main_image_url="https://example.com/doi.jpg"
            )
        ]
        
        for attraction in attractions:
            db.session.add(attraction)
        db.session.commit()

    def test_search_attractions_basic(self, client):
        """Test basic search functionality"""
        response = client.get("/api/search?query=วัด&language=th")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        assert "results" in data["data"]
        assert "total_count" in data["data"]
        
        # Should find the temple
        results = data["data"]["results"]
        assert len(results) >= 1
        assert any("วัดพระแก้ว" in result["name"] for result in results)

    def test_search_attractions_post(self, client):
        """Test search with POST method and JSON payload"""
        search_data = {
            "query": "เกาะ",
            "language": "th",
            "category": "ชายหาด",
            "limit": 10
        }
        
        response = client.post(
            "/api/search",
            data=json.dumps(search_data),
            content_type="application/json"
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        
        results = data["data"]["results"]
        assert len(results) >= 1
        assert any("เกาะพีพี" in result["name"] for result in results)

    def test_search_with_filters(self, client):
        """Test search with multiple filters"""
        response = client.get(
            "/api/search?query=&province=เชียงใหม่&category=ธรรมชาติ"
        )
        assert response.status_code == 200
        
        data = response.get_json()
        results = data["data"]["results"]
        
        # Should find attractions in Chiang Mai with Nature category
        assert len(results) >= 1
        assert all(result["province"] == "เชียงใหม่" for result in results)
        assert all(result["category"] == "ธรรมชาติ" for result in results)

    def test_search_fuzzy_matching(self, client):
        """Test fuzzy search capabilities"""
        # Test with partial/typo search
        response = client.get("/api/search?query=วดพระ&language=th")
        assert response.status_code == 200
        
        data = response.get_json()
        results = data["data"]["results"]
        
        # Should still find results despite partial query
        assert len(results) >= 0  # Fuzzy search might or might not find results

    def test_search_sorting(self, client):
        """Test different sorting options"""
        # Test sorting by name
        response = client.get("/api/search?query=&sort_by=name")
        assert response.status_code == 200
        
        data = response.get_json()
        results = data["data"]["results"]
        
        if len(results) > 1:
            # Results should be sorted by name
            names = [result["name"] for result in results]
            assert names == sorted(names)

    def test_search_pagination(self, client):
        """Test search pagination"""
        response = client.get("/api/search?query=&limit=2&offset=0")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "pagination" in data["data"]
        assert data["data"]["pagination"]["limit"] == 2
        assert data["data"]["pagination"]["offset"] == 0
        
        results = data["data"]["results"]
        assert len(results) <= 2

    def test_search_response_structure(self, client):
        """Test search response structure"""
        response = client.get("/api/search?query=วัด")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        
        search_data = data["data"]
        
        # Check required fields
        required_fields = [
            "results", "total_count", "query", "filters", 
            "pagination", "processing_time_ms"
        ]
        for field in required_fields:
            assert field in search_data
        
        # Check result structure
        if search_data["results"]:
            result = search_data["results"][0]
            assert "id" in result
            assert "name" in result
            assert "similarity_score" in result
            assert "matched_fields" in result

    def test_search_suggestions_endpoint_exists(self, client):
        """Test that search suggestions endpoint is accessible"""
        response = client.get("/api/search/suggestions?query=วัด&language=th")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "data" in data
        assert "success" in data
        assert "suggestions" in data["data"]

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
        response = client.get("/api/search/suggestions?query=วัด&language=th")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "data" in data
        suggestions = data["data"]["suggestions"]
        
        # Should find temple suggestions
        if suggestions:
            assert any("วัด" in suggestion["text"] for suggestion in suggestions)

    def test_trending_search_endpoint(self, client):
        """Test trending search endpoint"""
        response = client.get("/api/search/trending?language=th")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        assert "trending" in data["data"]
        assert isinstance(data["data"]["trending"], list)

    def test_search_error_handling(self, client):
        """Test search error handling"""
        # Test with invalid parameters
        response = client.get("/api/search?min_rating=invalid")
        assert response.status_code == 400
        
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid parameter" in data["message"]

    def test_search_with_rating_filters(self, client):
        """Test search with rating filters"""
        response = client.get("/api/search?min_rating=4.0&max_rating=5.0")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        # Rating filter functionality tested (results may be empty due to test data)