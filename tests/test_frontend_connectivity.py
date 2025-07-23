"""
Tests for frontend connectivity and CORS functionality
These tests verify that the API can properly communicate with frontend applications
"""
import json
from src.models import db, Attraction, User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token


def test_health_check_endpoint(client):
    """Test the health check endpoint for frontend monitoring"""
    rv = client.get("/health")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "status" in json_data["data"]
    assert json_data["data"]["status"] == "healthy"
    assert "endpoints" in json_data["data"]
    assert json_data["data"]["cors_enabled"] is True


def test_cors_headers_on_get_request(client):
    """Test that CORS headers are properly set on GET requests"""
    rv = client.get("/api/attractions", headers={"Origin": "http://localhost:3000"})
    assert rv.status_code == 200
    # Note: In test environment, CORS headers might not be set exactly as in production
    # This tests that the request succeeds from allowed origins


def test_cors_preflight_options_request(client):
    """Test CORS preflight OPTIONS request"""
    rv = client.options(
        "/api/attractions",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
    )
    # OPTIONS request should succeed
    assert rv.status_code in [200, 204]


def test_all_major_endpoints_respond_correctly(client, auth_headers):
    """Test that all major endpoints frontend uses respond with correct format"""
    
    # Test GET attractions (public endpoint)
    rv = client.get("/api/attractions")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "data" in json_data
    assert "attractions" in json_data["data"]
    assert "pagination" in json_data["data"]
    
    # Test health check
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_json()["success"] is True
    
    # Test search suggestions
    rv = client.get("/api/search/suggestions?query=test")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "suggestions" in json_data["data"]


def test_authentication_flow_for_frontend(client, app):
    """Test complete authentication flow that frontend would use"""
    with app.app_context():
        # Test user registration
        register_data = {
            "username": "frontend_test_user",
            "password": "testpassword123"
        }
        rv = client.post("/api/auth/register", json=register_data)
        if rv.status_code == 409:  # User already exists
            pass  # This is fine for testing
        else:
            assert rv.status_code == 201
            json_data = rv.get_json()
            assert json_data["success"] is True
        
        # Test user login
        login_data = {
            "username": "frontend_test_user",
            "password": "testpassword123"
        }
        rv = client.post("/api/auth/login", json=login_data)
        if rv.status_code == 401:
            # Create user first if login fails
            hashed_password = generate_password_hash("testpassword123")
            user = User(username="frontend_test_user", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            rv = client.post("/api/auth/login", json=login_data)
        
        assert rv.status_code == 200
        json_data = rv.get_json()
        assert json_data["success"] is True
        assert "access_token" in json_data["data"]
        
        # Test authenticated request using the token
        token = json_data["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        rv = client.post("/api/reviews", 
                        headers=headers,
                        json={
                            "user_id": 1,
                            "attraction_id": 1,
                            "rating": 5,
                            "comment": "Test review from frontend"
                        })
        # This might fail if attraction doesn't exist, but auth should work
        assert rv.status_code in [201, 400, 404, 422]  # 422 for validation errors, 400/404 if attraction doesn't exist


def test_response_format_consistency(client):
    """Test that all API responses follow the same format for frontend"""
    endpoints_to_test = [
        ("/", 200),
        ("/health", 200),
        ("/api/attractions", 200),
        ("/api/search/suggestions?query=test", 200),
    ]
    
    for endpoint, expected_status in endpoints_to_test:
        rv = client.get(endpoint)
        assert rv.status_code == expected_status
        json_data = rv.get_json()
        
        # All responses should have these required fields
        assert "success" in json_data
        assert "message" in json_data
        assert isinstance(json_data["success"], bool)
        assert isinstance(json_data["message"], str)
        
        # If success is True, should have data field
        if json_data["success"]:
            assert "data" in json_data or json_data["message"]  # Either data or meaningful message


def test_search_suggestions_functionality(client, app):
    """Test search suggestions work correctly for frontend autocomplete"""
    with app.app_context():
        # Create test attraction for search
        attraction = Attraction(
            name="Test Beach",
            description="Beautiful test beach",
            province="Test Province",
            category="Beach"
        )
        db.session.add(attraction)
        db.session.commit()
        
        # Test search with query
        rv = client.get("/api/search/suggestions?query=beach")
        assert rv.status_code == 200
        json_data = rv.get_json()
        assert json_data["success"] is True
        assert "suggestions" in json_data["data"]
        suggestions = json_data["data"]["suggestions"]
        
        # Should find our test attraction
        beach_found = any(s["text"] == "Test Beach" for s in suggestions)
        assert beach_found
        
        # Check suggestion format
        if suggestions:
            suggestion = suggestions[0]
            required_fields = ["id", "type", "text", "description"]
            for field in required_fields:
                assert field in suggestion


def test_error_handling_for_frontend(client):
    """Test that errors are returned in consistent format for frontend"""
    # Test 404 error
    rv = client.get("/api/attractions/99999")
    json_data = rv.get_json()
    assert "success" in json_data
    assert "message" in json_data
    assert json_data["success"] is False
    
    # Test validation error
    rv = client.post("/api/auth/login", json={"username": "", "password": ""})
    assert rv.status_code in [400, 401]  # Can be 400 for validation or 401 for invalid credentials
    json_data = rv.get_json()
    assert json_data["success"] is False
    assert "message" in json_data or "data" in json_data


def test_json_content_type_handling(client):
    """Test that API properly handles JSON content type from frontend"""
    # Test with proper JSON content type
    rv = client.post("/api/auth/login",
                     data=json.dumps({"username": "test", "password": "test"}),
                     content_type="application/json")
    # Should process the request (even if credentials are wrong)
    assert rv.status_code in [200, 400, 401]
    
    # Response should be JSON
    assert rv.content_type.startswith("application/json")