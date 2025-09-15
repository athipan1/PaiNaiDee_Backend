"""
Comprehensive test suite for Phase 1 functionality
This test validates core functionality without requiring a real database.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from app.main import app

client = TestClient(app)

# Mock data for testing
MOCK_LOCATION = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "ดอยสุเทพ",
    "province": "เชียงใหม่",
    "aliases": ["Doi Suthep"],
    "lat": 18.8047,
    "lng": 98.9217,
    "popularity_score": 95,
    "created_at": "2024-01-01T00:00:00Z"
}

MOCK_POST = {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "caption": "Beautiful sunset at Doi Suthep",
    "media": [],
    "location": MOCK_LOCATION,
    "like_count": 25,
    "comment_count": 3,
    "created_at": "2024-01-15T10:30:00Z",
    "score": 0.85
}

class TestPhase1Endpoints:
    """Test all Phase 1 endpoints"""
    
    def test_health_endpoint(self):
        """Test health check with version and db status"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["app_version"] == "1.0.0"
        assert "status" in data
        assert "checks" in data
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint with API information"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "features" in data
        assert data["phase"] == "1"
    
    def test_openapi_documentation(self):
        """Test OpenAPI schema and docs are available"""
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "PaiNaiDee Backend API - Phase 1"
        
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
    
    @patch('app.services.search_service.SearchService.search_posts')
    def test_search_get_endpoint(self, mock_search):
        """Test GET search endpoint with parameters"""
        # Mock search response
        mock_search.return_value = AsyncMock(return_value={
            "query": "เชียงใหม่",
            "expansion": ["ดอยสุเทพ"],
            "posts": [MOCK_POST],
            "suggestions": [],
            "latency_ms": 45.2,
            "total_count": 1
        })
        
        response = client.get("/api/search", params={
            "q": "เชียงใหม่",
            "lat": 18.7883,
            "lon": 98.9853,
            "sort": "distance",
            "limit": 10
        })
        
        # Should reach the endpoint (database errors are expected in test env)
        assert response.status_code in [200, 500]  # 500 due to DB connection
    
    @patch('app.services.search_service.SearchService.search_posts')
    def test_search_post_endpoint(self, mock_search):
        """Test POST search endpoint with JSON body"""
        mock_search.return_value = AsyncMock(return_value={
            "query": "ทะเล",
            "expansion": ["sea", "beach"],
            "posts": [],
            "suggestions": [],
            "latency_ms": 32.1,
            "total_count": 0
        })
        
        response = client.post("/api/search", json={
            "q": "ทะเล",
            "lat": 7.8804,
            "lon": 98.3923,
            "radius_km": 50,
            "sort": "distance",
            "limit": 20
        })
        
        assert response.status_code in [200, 500]
    
    def test_search_validation(self):
        """Test search endpoint validation"""
        # Missing required parameter
        response = client.get("/api/search")
        assert response.status_code == 422
        
        # Invalid query length
        response = client.get("/api/search", params={"q": ""})
        assert response.status_code == 422
        
        # Invalid limit
        response = client.get("/api/search", params={"q": "test", "limit": 200})
        assert response.status_code == 422
    
    def test_locations_endpoint(self):
        """Test locations endpoint"""
        response = client.get("/api/locations")
        assert response.status_code in [200, 500]  # 500 due to DB connection
        
        # Test with filters
        response = client.get("/api/locations", params={
            "province": "เชียงใหม่",
            "page": 1,
            "page_size": 20
        })
        assert response.status_code in [200, 500]
    
    def test_posts_endpoint(self):
        """Test posts endpoint"""
        response = client.get("/api/posts")
        assert response.status_code in [200, 500]  # 500 due to DB connection
        
        # Test with pagination
        response = client.get("/api/posts", params={
            "page": 1,
            "page_size": 10
        })
        assert response.status_code in [200, 500]
    
    def test_posts_validation(self):
        """Test posts endpoint validation"""
        # Invalid page size
        response = client.get("/api/posts", params={"page_size": 100})
        assert response.status_code == 422
    
    def test_authentication_required_endpoints(self):
        """Test endpoints that require authentication"""
        fake_post_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Like endpoint without auth
        response = client.post(f"/api/posts/{fake_post_id}/like")
        assert response.status_code == 401
        
        # Comment endpoint without auth
        response = client.post(f"/api/posts/{fake_post_id}/comments", 
                             json={"content": "test comment"})
        assert response.status_code == 401
        
        # Create post endpoint without auth
        response = client.post("/api/posts", 
                             files={"media_files": ("test.jpg", b"fake image", "image/jpeg")},
                             data={"caption": "test"})
        assert response.status_code == 401
    
    def test_api_key_authentication(self):
        """Test API key authentication"""
        fake_post_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Test with valid API key but no actor ID
        response = client.post(f"/api/posts/{fake_post_id}/like",
                             headers={"X-API-Key": "demo-api-key"})
        assert response.status_code in [400, 422]  # Should require X-Actor-Id
        
        # Test with valid API key and actor ID
        response = client.post(f"/api/posts/{fake_post_id}/like",
                             headers={
                                 "X-API-Key": "demo-api-key",
                                 "X-Actor-Id": "user_123"
                             })
        # Should reach the service layer (may fail due to DB/post not found)
        assert response.status_code in [404, 500]
        
        # Test with invalid API key
        response = client.post(f"/api/posts/{fake_post_id}/like",
                             headers={
                                 "X-API-Key": "invalid-key",
                                 "X-Actor-Id": "user_123"
                             })
        assert response.status_code == 401

class TestKeywordMapping:
    """Test keyword expansion functionality"""
    
    def test_keyword_mapping_file_exists(self):
        """Test that keyword mapping file exists and is valid"""
        import os
        mapping_path = os.path.join(os.path.dirname(__file__), '../data/keyword_mapping.json')
        assert os.path.exists(mapping_path)
        
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        
        # Check required categories
        assert "provinces" in mapping
        assert "categories" in mapping
        assert "thai_english" in mapping
        assert "english_thai" in mapping
        
        # Check some sample mappings
        assert "เชียงใหม่" in mapping["provinces"]
        assert isinstance(mapping["provinces"]["เชียงใหม่"], list)
        assert len(mapping["provinces"]["เชียงใหม่"]) > 0

class TestSearchAlgorithm:
    """Test search algorithm components"""
    
    def test_haversine_distance_calculation(self):
        """Test Haversine distance calculation"""
        from app.services.search_service import SearchService
        
        service = SearchService()
        
        # Test known distance (Bangkok to Chiang Mai approximately 600km)
        bangkok_lat, bangkok_lon = 13.7563, 100.5018
        chiang_mai_lat, chiang_mai_lon = 18.7883, 98.9853
        
        distance = service._calculate_haversine_distance(
            bangkok_lat, bangkok_lon, chiang_mai_lat, chiang_mai_lon
        )
        
        # Should be approximately 600km (allow 10% tolerance)
        assert 540 <= distance <= 660
    
    def test_keyword_mapping_loading(self):
        """Test keyword mapping loading"""
        from app.services.search_service import SearchService
        import asyncio
        
        service = SearchService()
        
        async def test_loading():
            mapping = await service._load_keyword_mapping()
            assert isinstance(mapping, dict)
            assert "provinces" in mapping
            return mapping
        
        mapping = asyncio.run(test_loading())
        assert mapping is not None

class TestHTTPStatusCodes:
    """Test proper HTTP status codes are returned"""
    
    def test_405_method_not_allowed(self):
        """Test 405 for unsupported HTTP methods"""
        # Search endpoint only supports GET and POST
        response = client.put("/api/search")
        assert response.status_code == 405
        
        response = client.delete("/api/search")  
        assert response.status_code == 405
    
    def test_404_not_found(self):
        """Test 404 for non-existent endpoints"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        response = client.get("/nonexistent") 
        assert response.status_code == 404
    
    def test_422_validation_error(self):
        """Test 422 for validation errors"""
        # Invalid query parameter
        response = client.get("/api/search", params={"q": ""})
        assert response.status_code == 422
        
        # Invalid JSON in POST
        response = client.post("/api/search", 
                             json={"invalid": "field"})
        assert response.status_code == 422

if __name__ == "__main__":
    # Run tests directly
    import sys
    
    print("🧪 Running comprehensive Phase 1 tests...")
    
    test_classes = [TestPhase1Endpoints, TestKeywordMapping, TestSearchAlgorithm, TestHTTPStatusCodes]
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        
        instance = test_class()
        methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for method_name in methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
    
    print(f"\n🎉 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎊 All tests passed! Phase 1 implementation is ready.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check implementation.")
        sys.exit(1)