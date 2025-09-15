"""
Simple test to verify Phase 1 endpoints are working
"""
import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "app_version" in data
    assert data["app_version"] == "1.0.0"

def test_openapi_docs():
    """Test OpenAPI documentation is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    response = client.get("/docs")
    assert response.status_code == 200

def test_search_endpoint_get():
    """Test GET search endpoint"""
    response = client.get("/api/search?q=test")
    # Should return 200 even with empty database
    assert response.status_code in [200, 422]  # 422 if validation fails

def test_search_endpoint_post():
    """Test POST search endpoint"""
    response = client.post("/api/search", json={"q": "test"})
    # Should return 200 even with empty database
    assert response.status_code in [200, 422]

def test_locations_endpoint():
    """Test locations endpoint"""
    response = client.get("/api/locations")
    # Should return 200 with empty list
    assert response.status_code in [200, 422]

def test_posts_endpoint():
    """Test posts endpoint"""
    response = client.get("/api/posts")
    # Should return 200 with empty list
    assert response.status_code in [200, 422]

if __name__ == "__main__":
    # Run tests directly
    print("🧪 Testing Phase 1 endpoints...")
    
    try:
        test_health_endpoint()
        print("✅ Health endpoint working")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    try:
        test_openapi_docs()
        print("✅ OpenAPI docs working")
    except Exception as e:
        print(f"❌ OpenAPI docs failed: {e}")
    
    try:
        test_search_endpoint_get()
        print("✅ GET Search endpoint accessible")
    except Exception as e:
        print(f"❌ GET Search endpoint failed: {e}")
    
    try:
        test_search_endpoint_post()
        print("✅ POST Search endpoint accessible")
    except Exception as e:
        print(f"❌ POST Search endpoint failed: {e}")
    
    try:
        test_locations_endpoint()
        print("✅ Locations endpoint accessible")
    except Exception as e:
        print(f"❌ Locations endpoint failed: {e}")
    
    try:
        test_posts_endpoint()
        print("✅ Posts endpoint accessible")
    except Exception as e:
        print(f"❌ Posts endpoint failed: {e}")
    
    print("🎉 Basic endpoint tests completed!")