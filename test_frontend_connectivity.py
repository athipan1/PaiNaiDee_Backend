#!/usr/bin/env python3
"""
Manual testing script for frontend connectivity verification
This script tests the API using SQLite to avoid PostgreSQL dependency
"""
import os
import sys
import time
import requests
import json
from multiprocessing import Process

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_test_app():
    """Create app with SQLite for testing"""
    from src.app import create_app
    from src.models import db, Attraction, User
    from werkzeug.security import generate_password_hash
    
    # Use testing config which uses SQLite
    app = create_app("testing")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create test data
        # Test user
        test_user = User(
            username="testuser",
            password=generate_password_hash("testpass123")
        )
        db.session.add(test_user)
        
        # Test attractions
        attractions = [
            Attraction(
                name="วัดพระแก้ว",
                description="วัดที่สวยงามในกรุงเทพ",
                province="กรุงเทพมหานคร",
                category="วัด",
                latitude=13.7563,
                longitude=100.5018
            ),
            Attraction(
                name="เกาะสมุย",
                description="เกาะสวยงามในทะเลไทย",
                province="สุราษฎร์ธานี",
                category="เกาะ",
                latitude=9.5380,
                longitude=100.0211
            ),
            Attraction(
                name="ดอยสุเทพ",
                description="ภูเขาสูงในเชียงใหม่",
                province="เชียงใหม่",
                category="ภูเขา",
                latitude=18.8047,
                longitude=98.9217
            )
        ]
        
        for attraction in attractions:
            db.session.add(attraction)
        
        db.session.commit()
        print("Test data created successfully!")
    
    return app

def run_test_server():
    """Run test server"""
    app = create_test_app()
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)

def test_api_endpoints():
    """Test all API endpoints for frontend connectivity"""
    base_url = "http://localhost:5000"
    headers = {
        "Origin": "http://localhost:3000",
        "Content-Type": "application/json"
    }
    
    print("Testing API endpoints for frontend connectivity...")
    print("=" * 50)
    
    # Wait for server to start
    time.sleep(2)
    
    # Test 1: Health check
    print("1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Home endpoint
    print("2. Testing home endpoint...")
    try:
        response = requests.get(f"{base_url}/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: Get attractions
    print("3. Testing attractions endpoint...")
    try:
        response = requests.get(f"{base_url}/api/attractions", headers=headers)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Success: {data.get('success')}")
        if data.get('success') and data.get('data'):
            print(f"   Attractions count: {len(data['data']['attractions'])}")
            if data['data']['attractions']:
                print(f"   First attraction: {data['data']['attractions'][0]['name']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 4: Search suggestions
    print("4. Testing search suggestions...")
    try:
        response = requests.get(f"{base_url}/api/search/suggestions?query=วัด", headers=headers)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Success: {data.get('success')}")
        if data.get('success') and data.get('data'):
            suggestions = data['data']['suggestions']
            print(f"   Suggestions count: {len(suggestions)}")
            if suggestions:
                print(f"   First suggestion: {suggestions[0]['text']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 5: Authentication flow
    print("5. Testing authentication flow...")
    try:
        # Login
        login_data = {"username": "testuser", "password": "testpass123"}
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, headers=headers)
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            if token_data.get('success') and 'access_token' in token_data.get('data', {}):
                token = token_data['data']['access_token']
                print(f"   Token received: {token[:20]}...")
                
                # Test authenticated endpoint
                auth_headers = headers.copy()
                auth_headers["Authorization"] = f"Bearer {token}"
                
                # Try to add a review (this might fail but should authenticate properly)
                review_data = {
                    "user_id": 1,
                    "attraction_id": 1,
                    "rating": 5,
                    "comment": "Great place for frontend testing!"
                }
                review_response = requests.post(f"{base_url}/api/reviews", json=review_data, headers=auth_headers)
                print(f"   Review endpoint status: {review_response.status_code}")
        else:
            print(f"   Login failed: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 6: CORS preflight (OPTIONS)
    print("6. Testing CORS preflight (OPTIONS)...")
    try:
        options_headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        response = requests.options(f"{base_url}/api/attractions", headers=options_headers)
        print(f"   Status: {response.status_code}")
        print(f"   CORS headers present: {'Access-Control-Allow-Origin' in response.headers}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("Frontend connectivity testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    print("Starting API Frontend Connectivity Test")
    print("=" * 50)
    
    # Start server in background process
    server_process = Process(target=run_test_server)
    server_process.start()
    
    try:
        # Run tests
        test_api_endpoints()
    finally:
        # Clean up
        server_process.terminate()
        server_process.join()
        print("Test completed.")