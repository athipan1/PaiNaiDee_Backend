from src.models import db, PlaceDetail, Attraction
from flask import abort


class PlaceDetailService:
    @staticmethod
    def get_place_detail_by_place_id(place_id):
        """Get place detail by place (attraction) id"""
        # First verify the attraction exists
        attraction = db.session.get(Attraction, place_id)
        if not attraction:
            abort(404, description="Place not found.")
        
        # Get place detail for this attraction
        place_detail = PlaceDetail.query.filter_by(place_id=place_id).first()
        return place_detail

    @staticmethod
    def add_place_detail(place_id, data):
        """Add new place detail for a place (attraction)"""
        # First verify the attraction exists
        attraction = db.session.get(Attraction, place_id)
        if not attraction:
            abort(404, description="Place not found.")
        
        # Check if place detail already exists
        existing_detail = PlaceDetail.query.filter_by(place_id=place_id).first()
        if existing_detail:
            abort(400, description="Place detail already exists. Use PUT to update.")
        
        # Create new place detail
        place_detail = PlaceDetail(
            place_id=place_id,
            description=data.get('description'),
            link=data.get('link')
        )
        
        db.session.add(place_detail)
        db.session.commit()
        return place_detail

    @staticmethod
    def update_place_detail(place_id, data):
        """Update existing place detail"""
        # First verify the attraction exists
        attraction = db.session.get(Attraction, place_id)
        if not attraction:
            abort(404, description="Place not found.")
        
        # Get existing place detail
        place_detail = PlaceDetail.query.filter_by(place_id=place_id).first()
        if not place_detail:
            abort(404, description="Place detail not found.")
        
        # Update fields
        if 'description' in data:
            place_detail.description = data['description']
        if 'link' in data:
            place_detail.link = data['link']
        
        db.session.commit()
        return place_detail

    @staticmethod
    def delete_place_detail(place_id):
        """Delete place detail"""
        # First verify the attraction exists
        attraction = db.session.get(Attraction, place_id)
        if not attraction:
            abort(404, description="Place not found.")
        
        # Get existing place detail
        place_detail = PlaceDetail.query.filter_by(place_id=place_id).first()
        if not place_detail:
            abort(404, description="Place detail not found.")
        
        db.session.delete(place_detail)
        db.session.commit()
        return True