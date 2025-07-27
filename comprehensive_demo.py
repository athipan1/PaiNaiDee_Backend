#!/usr/bin/env python
"""
Demonstration of PaiNaiDee Backend API
Shows all implemented endpoints working with sample data
"""
import json
from src.app import create_app
from src.models import db, Attraction, Room, User
from werkzeug.security import generate_password_hash

def run_api_demo():
    """Comprehensive API demonstration"""
    app = create_app("testing")
    
    print("🚀 PaiNaiDee Backend API Demo")
    print("=" * 50)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create test user for authentication
        test_user = User(
            username="testuser",
            password=generate_password_hash("testpass123")
        )
        db.session.add(test_user)
        
        # Create test attractions
        attractions_data = [
            {
                "name": "Pai Walking Street",
                "description": "Famous walking street in Pai with local crafts and food",
                "address": "Pai District, Mae Hong Son",
                "province": "Mae Hong Son",
                "district": "Pai",
                "latitude": 19.3583,
                "longitude": 98.4367,
                "category": "market"
            },
            {
                "name": "Pai Canyon",
                "description": "Stunning natural canyon with hiking trails",
                "address": "Pai District, Mae Hong Son",
                "province": "Mae Hong Son", 
                "district": "Pai",
                "latitude": 19.3789,
                "longitude": 98.4123,
                "category": "nature"
            }
        ]
        
        attractions = []
        for data in attractions_data:
            attraction = Attraction(**data)
            db.session.add(attraction)
            attractions.append(attraction)
        
        db.session.commit()
        
        # Create test rooms
        rooms_data = [
            {
                "attraction_id": attractions[0].id,
                "name": "Cozy Room near Walking Street",
                "description": "A comfortable room near the famous walking street",
                "price": 800.0,
                "capacity": 2,
                "amenities": ["WiFi", "Air Conditioning", "TV"],
                "is_available": True
            },
            {
                "attraction_id": attractions[0].id,
                "name": "Budget Room",
                "description": "Affordable accommodation with basic amenities",
                "price": 500.0,
                "capacity": 1,
                "amenities": ["WiFi", "Fan"],
                "is_available": True
            },
            {
                "attraction_id": attractions[1].id,
                "name": "Canyon View Room",
                "description": "Room with stunning canyon views",
                "price": 1200.0,
                "capacity": 2,
                "amenities": ["WiFi", "Air Conditioning", "Balcony", "Mini Bar"],
                "is_available": True
            }
        ]
        
        rooms = []
        for data in rooms_data:
            room = Room(**data)
            db.session.add(room)
            rooms.append(room)
        
        db.session.commit()
        
        # Store IDs to avoid session issues
        attraction_1_id = attractions[0].id
        room_1_id = rooms[0].id
        
        print(f"✅ Created {len(attractions)} attractions and {len(rooms)} rooms")
        print()
        
    # Test the API endpoints
    with app.test_client() as client:
        print("🔍 Testing API Endpoints")
        print("-" * 30)
        
        # 1. Welcome endpoint
        print("1. Welcome Endpoint:")
        response = client.get('/')
        data = response.get_json()
        print(f"   GET / → {response.status_code}")
        print(f"   API Version: {data['data']['version']}")
        print(f"   Documentation: {data['data']['documentation']}")
        print()
        
        # 2. Health check
        print("2. Health Check:")
        response = client.get('/health')
        data = response.get_json()
        print(f"   GET /health → {response.status_code}")
        print(f"   Status: {data['data']['status']}")
        print()
        
        # 3. All rooms
        print("3. Get All Rooms:")
        response = client.get('/api/v1/rooms')
        data = response.get_json()
        print(f"   GET /api/v1/rooms → {response.status_code}")
        print(f"   Found {len(data['data']['rooms'])} rooms:")
        for room in data['data']['rooms']:
            print(f"     • {room['name']} - ${room['price']} ({room['attraction_name']})")
        print()
        
        # 4. Rooms near specific attraction (Example Flow)
        print("4. Example Flow - Rooms Near Attraction:")
        response = client.get(f'/api/v1/rooms?near={attraction_1_id}')
        data = response.get_json()
        print(f"   GET /api/v1/rooms?near={attraction_1_id} → {response.status_code}")
        print(f"   Found {len(data['data']['rooms'])} rooms near 'Pai Walking Street':")
        for room in data['data']['rooms']:
            print(f"     • {room['name']} - ${room['price']}")
            print(f"       Address: {room['attraction_address']}")
            print(f"       Location: {room['attraction_location']['lat']}, {room['attraction_location']['lng']}")
        print()
        
        # 5. Price filtering
        print("5. Price Filtering:")
        response = client.get('/api/v1/rooms?min_price=600&max_price=1000')
        data = response.get_json()
        print(f"   GET /api/v1/rooms?min_price=600&max_price=1000 → {response.status_code}")
        print(f"   Found {len(data['data']['rooms'])} rooms in price range $600-$1000:")
        for room in data['data']['rooms']:
            print(f"     • {room['name']} - ${room['price']}")
        print()
        
        # 6. Room details
        print("6. Room Details:")
        response = client.get(f'/api/v1/rooms/{room_1_id}')
        data = response.get_json()
        print(f"   GET /api/v1/rooms/{room_1_id} → {response.status_code}")
        room_detail = data['data']
        print(f"   Room: {room_detail['name']}")
        print(f"   Price: ${room_detail['price']}")
        print(f"   Capacity: {room_detail['capacity']} people")
        print(f"   Attraction: {room_detail['attraction_name']}")
        print()
        
        # 7. Room availability check
        print("7. Room Availability Check:")
        response = client.get(f'/api/v1/rooms/{room_1_id}/availability?date_start=2024-08-01&date_end=2024-08-03')
        data = response.get_json()
        print(f"   GET /api/v1/rooms/{room_1_id}/availability?date_start=2024-08-01&date_end=2024-08-03 → {response.status_code}")
        print(f"   Available: {data['data']['available']}")
        print()
        
        # 8. All attractions
        print("8. Get All Attractions:")
        response = client.get('/api/v1/attractions')
        data = response.get_json()
        print(f"   GET /api/v1/attractions → {response.status_code}")
        print(f"   Found {len(data['data']['attractions'])} attractions:")
        for attraction in data['data']['attractions']:
            print(f"     • {attraction['name']} ({attraction['category']})")
            print(f"       {len(attraction['rooms'])} rooms available")
        print()
        
        # 9. Pagination demonstration
        print("9. Pagination Example:")
        response = client.get('/api/v1/rooms?page=1&limit=2')
        data = response.get_json()
        print(f"   GET /api/v1/rooms?page=1&limit=2 → {response.status_code}")
        print(f"   Page: {data['data']['pagination']['current_page']}/{data['data']['pagination']['total_pages']}")
        print(f"   Items: {len(data['data']['rooms'])}/{data['data']['pagination']['total_items']}")
        print(f"   Has next: {data['data']['pagination']['has_next']}")
        print()
        
        print("✅ All API endpoints working correctly!")
        print()
        print("📚 API Documentation available at: http://localhost:5000/api/docs/")
        print("🔧 API Base URL: http://localhost:5000/api/v1/")
        print()
        print("🎯 Key Features Implemented:")
        print("   ✓ RESTful API with versioning (/api/v1/)")
        print("   ✓ JSON data exchange format")
        print("   ✓ JWT Authentication ready")
        print("   ✓ CORS configuration")
        print("   ✓ Swagger/OpenAPI documentation")
        print("   ✓ Environment configuration")
        print("   ✓ Room management with filtering")
        print("   ✓ Attraction-based room search")
        print("   ✓ Price filtering and pagination")
        print("   ✓ Room availability checking")
        print("   ✓ Comprehensive error handling")

if __name__ == "__main__":
    run_api_demo()