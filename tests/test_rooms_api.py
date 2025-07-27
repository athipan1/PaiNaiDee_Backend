import pytest
from src.app import create_app
from src.models import db, Room, Attraction


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def sample_attraction(app):
    """Create a sample attraction for testing."""
    with app.app_context():
        attraction = Attraction(
            name="Test Attraction",
            description="A test attraction",
            address="123 Test St",
            province="Test Province",
            district="Test District",
            latitude=18.7883,
            longitude=98.9853,
            category="test"
        )
        db.session.add(attraction)
        db.session.commit()
        # Refresh to ensure the object is properly attached
        db.session.refresh(attraction)
        attraction_id = attraction.id
        return attraction_id


@pytest.fixture
def sample_room(app, sample_attraction):
    """Create a sample room for testing."""
    with app.app_context():
        room = Room(
            attraction_id=sample_attraction,  # sample_attraction is now just the ID
            name="Test Room",
            description="A comfortable test room",
            price=1000.0,
            capacity=2,
            amenities=["WiFi", "Air Conditioning"],
            is_available=True
        )
        db.session.add(room)
        db.session.commit()
        db.session.refresh(room)
        room_id = room.id
        return room_id


class TestRoomsAPI:
    def test_get_all_rooms_empty(self, client):
        """Test getting all rooms when no rooms exist."""
        response = client.get('/api/v1/rooms')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['rooms'] == []
        assert data['data']['pagination']['total_items'] == 0

    def test_get_all_rooms_with_data(self, client, sample_room):
        """Test getting all rooms when rooms exist."""
        response = client.get('/api/v1/rooms')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']['rooms']) == 1
        assert data['data']['rooms'][0]['name'] == 'Test Room'
        assert data['data']['rooms'][0]['price'] == 1000.0

    def test_get_rooms_near_attraction(self, client, sample_room, sample_attraction):
        """Test filtering rooms near a specific attraction."""
        response = client.get(f'/api/v1/rooms?near={sample_attraction}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']['rooms']) == 1
        assert data['data']['rooms'][0]['attraction_id'] == sample_attraction

    def test_get_rooms_price_filter(self, client, sample_room):
        """Test filtering rooms by price range."""
        # Test min price filter
        response = client.get('/api/v1/rooms?min_price=500')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['rooms']) == 1
        
        # Test max price filter that excludes the room
        response = client.get('/api/v1/rooms?max_price=500')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['rooms']) == 0

    def test_get_room_detail(self, client, sample_room):
        """Test getting detailed information about a specific room."""
        response = client.get(f'/api/v1/rooms/{sample_room}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == sample_room
        assert data['data']['name'] == 'Test Room'

    def test_get_room_detail_not_found(self, client):
        """Test getting room detail for non-existent room."""
        response = client.get('/api/v1/rooms/999')
        assert response.status_code == 404

    def test_room_pagination(self, client, app, sample_attraction):
        """Test room pagination."""
        with app.app_context():
            # Create multiple rooms
            for i in range(15):
                room = Room(
                    attraction_id=sample_attraction,  # sample_attraction is now just the ID
                    name=f"Room {i}",
                    price=1000.0 + i * 100,
                    capacity=2
                )
                db.session.add(room)
            db.session.commit()

        # Test first page
        response = client.get('/api/v1/rooms?page=1&limit=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['rooms']) == 10
        assert data['data']['pagination']['total_items'] == 15
        assert data['data']['pagination']['total_pages'] == 2
        assert data['data']['pagination']['has_next'] is True

        # Test second page
        response = client.get('/api/v1/rooms?page=2&limit=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['rooms']) == 5
        assert data['data']['pagination']['has_next'] is False