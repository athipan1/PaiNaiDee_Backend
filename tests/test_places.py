import pytest
import json
from src.models import Attraction, PlaceDetail


class TestPlacesRoutes:
    def test_get_place_detail_exists(self, client, app):
        """Test getting place details for existing attraction"""
        with app.app_context():
            # Create a test attraction
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            attraction_id = attraction.id

        response = client.get(f"/api/places/{attraction_id}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["name"] == "Test Place"
        assert data["data"]["place_detail"] is None  # No place detail added yet

    def test_get_place_detail_not_found(self, client):
        """Test getting place details for non-existent attraction"""
        response = client.get("/api/places/999")
        assert response.status_code == 404

    def test_add_place_details_success(self, client, app, auth_headers):
        """Test adding place details successfully"""
        with app.app_context():
            # Create a test attraction
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            attraction_id = attraction.id

        place_detail_data = {
            "description": "Additional place description",
            "link": "https://example.com"
        }

        response = client.post(
            f"/api/places/{attraction_id}/details",
            data=json.dumps(place_detail_data),
            content_type="application/json",
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["description"] == "Additional place description"
        assert data["data"]["link"] == "https://example.com"

    def test_add_place_details_unauthorized(self, client, app):
        """Test adding place details without authentication"""
        with app.app_context():
            # Create a test attraction
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            attraction_id = attraction.id

        place_detail_data = {
            "description": "Additional place description",
            "link": "https://example.com"
        }

        response = client.post(
            f"/api/places/{attraction_id}/details",
            data=json.dumps(place_detail_data),
            content_type="application/json"
        )
        
        assert response.status_code == 401

    def test_add_place_details_place_not_found(self, client, auth_headers):
        """Test adding place details for non-existent place"""
        place_detail_data = {
            "description": "Additional place description",
            "link": "https://example.com"
        }

        response = client.post(
            "/api/places/999/details",
            data=json.dumps(place_detail_data),
            content_type="application/json",
            headers=auth_headers
        )
        
        assert response.status_code == 400

    def test_add_place_details_already_exists(self, client, app, auth_headers):
        """Test adding place details when they already exist"""
        with app.app_context():
            # Create a test attraction
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            
            # Add place detail
            place_detail = PlaceDetail(
                place_id=attraction.id,
                description="Existing description",
                link="https://existing.com"
            )
            db.session.add(place_detail)
            db.session.commit()
            attraction_id = attraction.id

        place_detail_data = {
            "description": "New description",
            "link": "https://new.com"
        }

        response = client.post(
            f"/api/places/{attraction_id}/details",
            data=json.dumps(place_detail_data),
            content_type="application/json",
            headers=auth_headers
        )
        
        assert response.status_code == 400

    def test_update_place_details_success(self, client, app, auth_headers):
        """Test updating place details successfully"""
        with app.app_context():
            # Create a test attraction
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            
            # Add place detail
            place_detail = PlaceDetail(
                place_id=attraction.id,
                description="Original description",
                link="https://original.com"
            )
            db.session.add(place_detail)
            db.session.commit()
            attraction_id = attraction.id

        updated_data = {
            "description": "Updated description",
            "link": "https://updated.com"
        }

        response = client.put(
            f"/api/places/{attraction_id}/details",
            data=json.dumps(updated_data),
            content_type="application/json",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["description"] == "Updated description"
        assert data["data"]["link"] == "https://updated.com"

    def test_update_place_details_not_found(self, client, app, auth_headers):
        """Test updating place details that don't exist"""
        with app.app_context():
            # Create a test attraction without place details
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            attraction_id = attraction.id

        updated_data = {
            "description": "Updated description",
            "link": "https://updated.com"
        }

        response = client.put(
            f"/api/places/{attraction_id}/details",
            data=json.dumps(updated_data),
            content_type="application/json",
            headers=auth_headers
        )
        
        assert response.status_code == 400

    def test_delete_place_details_success(self, client, app, auth_headers):
        """Test deleting place details successfully"""
        with app.app_context():
            # Create a test attraction
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            
            # Add place detail
            place_detail = PlaceDetail(
                place_id=attraction.id,
                description="To be deleted",
                link="https://delete.com"
            )
            db.session.add(place_detail)
            db.session.commit()
            attraction_id = attraction.id

        response = client.delete(
            f"/api/places/{attraction_id}/details",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_delete_place_details_not_found(self, client, app, auth_headers):
        """Test deleting place details that don't exist"""
        with app.app_context():
            # Create a test attraction without place details
            attraction = Attraction(
                name="Test Place",
                description="Test description",
                province="Test Province",
                category="Test Category"
            )
            from src.models import db
            db.session.add(attraction)
            db.session.commit()
            attraction_id = attraction.id

        response = client.delete(
            f"/api/places/{attraction_id}/details",
            headers=auth_headers
        )
        
        assert response.status_code == 400