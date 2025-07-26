"""
API Testing Script for Place Details Feature
This script demonstrates the new place details functionality.
"""

import requests
import json
import time


BASE_URL = "http://localhost:5000/api"


def print_response(response, operation):
    """Pretty print response"""
    print(f"\n{operation}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)


def test_place_details_api():
    """Test the place details API functionality"""
    
    print("🚀 Testing PaiNaiDee Place Details API")
    print("=" * 50)
    
    # Test 1: Check API is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/")
        print_response(response, "1. API Health Check")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:5000")
        print("Run: FLASK_ENV=testing python -m src.app")
        return
    
    # Test 2: Try to get a non-existent place
    response = requests.get(f"{BASE_URL}/places/999")
    print_response(response, "2. Get Non-existent Place (Expected 404)")
    
    # Test 3: Try to add place details without authentication
    place_detail_data = {
        "description": "Test place description",
        "link": "https://example.com"
    }
    
    response = requests.post(
        f"{BASE_URL}/places/1/details",
        json=place_detail_data
    )
    print_response(response, "3. Add Place Details Without Auth (Expected 401)")
    
    # Test 4: Test with invalid data
    invalid_data = {
        "description": "a" * 1000,  # Very long description 
        "link": "invalid-url"
    }
    
    # Since we don't have real authentication in this demo, 
    # we'll show what the request would look like
    print("\n4. Example Request with Authentication:")
    print("POST /api/places/1/details")
    print("Headers: {'Authorization': 'Bearer <jwt_token>', 'Content-Type': 'application/json'}")
    print(f"Body: {json.dumps(place_detail_data, indent=2)}")
    print("-" * 50)
    
    # Test 5: Show the expected successful response format
    print("\n5. Expected Successful Response Format:")
    success_response = {
        "success": True,
        "message": "Place details added successfully.",
        "data": {
            "id": 1,
            "place_id": 1,
            "description": "Test place description",
            "link": "https://example.com"
        }
    }
    print(f"Status: 201")
    print(f"Response: {json.dumps(success_response, indent=2)}")
    print("-" * 50)
    
    # Test 6: Show updated place response format
    print("\n6. Updated Place Response Format (includes place_detail):")
    place_response = {
        "success": True,
        "message": "Place retrieved successfully.",
        "data": {
            "id": 1,
            "name": "Sample Place",
            "description": "Original place description",
            "address": "123 Test Street",
            "province": "Test Province",
            "district": "Test District",
            "location": {"lat": 0.0, "lng": 0.0},
            "category": "Attraction",
            "opening_hours": "9:00-18:00",
            "entrance_fee": "Free",
            "contact_phone": "123-456-7890",
            "website": "https://place.com",
            "images": [],
            "rooms": [],
            "cars": [],
            "average_rating": 0.0,
            "total_reviews": 0,
            "place_detail": {
                "id": 1,
                "place_id": 1,
                "description": "Additional place description with more details",
                "link": "https://example.com/more-info"
            }
        }
    }
    print(f"Status: 200")
    print(f"Response: {json.dumps(place_response, indent=2)}")
    print("-" * 50)


def show_api_documentation():
    """Show API documentation"""
    print("\n📚 PaiNaiDee Place Details API Documentation")
    print("=" * 50)
    
    endpoints = [
        {
            "method": "GET",
            "path": "/api/places/:id",
            "description": "Get place details (alias to attractions with place_detail field)",
            "auth": "None",
            "response": "Place object with optional place_detail field"
        },
        {
            "method": "POST", 
            "path": "/api/places/:id/details",
            "description": "Add additional details for a place",
            "auth": "Bearer JWT token required",
            "body": {"description": "string (optional)", "link": "string (optional)"},
            "response": "Created place detail object"
        },
        {
            "method": "PUT",
            "path": "/api/places/:id/details", 
            "description": "Update existing place details",
            "auth": "Bearer JWT token required",
            "body": {"description": "string (optional)", "link": "string (optional)"},
            "response": "Updated place detail object"
        },
        {
            "method": "DELETE",
            "path": "/api/places/:id/details",
            "description": "Delete place details",
            "auth": "Bearer JWT token required", 
            "response": "Success message"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"Description: {endpoint['description']}")
        print(f"Authentication: {endpoint['auth']}")
        if 'body' in endpoint:
            print(f"Request Body: {json.dumps(endpoint['body'], indent=2)}")
        print(f"Response: {endpoint['response']}")
        print("-" * 30)


if __name__ == "__main__":
    print("🎯 PaiNaiDee Backend - Place Details Feature Demo")
    print("This script demonstrates the new place details API functionality.\n")
    
    # Show API documentation
    show_api_documentation()
    
    # Test the API
    test_place_details_api()
    
    print("\n✨ Demo completed!")
    print("\nTo test with real data:")
    print("1. Start the server: FLASK_ENV=testing python -m src.app")
    print("2. Create a test attraction using POST /api/attractions")
    print("3. Get a JWT token using POST /api/auth/login")
    print("4. Use the token to test the place details endpoints")
    print("\nFor frontend integration:")
    print("- The place_detail field will be included in all place/attraction responses")
    print("- Use the dedicated /places/:id/details endpoints to manage additional details")
    print("- All modification endpoints require JWT authentication")