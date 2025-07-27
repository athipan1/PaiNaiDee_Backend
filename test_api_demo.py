#!/usr/bin/env python
import os
from src.app import create_app
from src.models import db, Attraction, Room

def test_api():
    """Test the API with some sample data"""
    app = create_app("testing")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create test data
        attraction = Attraction(
            name="Pai Walking Street",
            description="Famous walking street in Pai",
            address="Pai District, Mae Hong Son",
            province="Mae Hong Son",
            district="Pai",
            latitude=19.3583,
            longitude=98.4367,
            category="market"
        )
        db.session.add(attraction)
        db.session.commit()
        
        # Create test rooms
        room1 = Room(
            attraction_id=attraction.id,
            name="Cozy Room near Walking Street",
            description="A comfortable room near the famous walking street",
            price=800.0,
            capacity=2,
            amenities=["WiFi", "Air Conditioning", "TV"],
            is_available=True
        )
        
        room2 = Room(
            attraction_id=attraction.id,
            name="Budget Room",
            description="Affordable accommodation",
            price=500.0,
            capacity=1,
            amenities=["WiFi", "Fan"],
            is_available=True
        )
        
        db.session.add(room1)
        db.session.add(room2)
        db.session.commit()
        
        print(f"Created attraction: {attraction.name} (ID: {attraction.id})")
        print(f"Created room 1: {room1.name} (ID: {room1.id})")
        print(f"Created room 2: {room2.name} (ID: {room2.id})")
        
    # Test the API endpoints
    with app.test_client() as client:
        print("\n=== Testing API Endpoints ===")
        
        # Test health check
        response = client.get('/health')
        print(f"Health check: {response.status_code} - {response.get_json()}")
        
        # Test rooms endpoint
        response = client.get('/api/v1/rooms')
        print(f"Rooms endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"  Found {len(data['data']['rooms'])} rooms")
            for room in data['data']['rooms']:
                print(f"    Room: {room['name']} - ${room['price']}")
        else:
            print(f"  Error: {response.get_json()}")
        
        # Test rooms near attraction
        response = client.get(f'/api/v1/rooms?near={attraction.id}')
        print(f"Rooms near attraction {attraction.id}: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"  Found {len(data['data']['rooms'])} rooms near attraction")
        
        # Test attractions endpoint
        response = client.get('/api/v1/attractions')
        print(f"Attractions endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"  Found {len(data['data']['attractions'])} attractions")

if __name__ == "__main__":
    test_api()