import os
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_current_user
from werkzeug.utils import secure_filename
from src.models import db, Attraction
from src.utils import standardized_response

attractions_bp = Blueprint('attractions', __name__)

@attractions_bp.route('/attractions', methods=['GET'])
def get_all_attractions():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    query = Attraction.query

    if q := request.args.get('q'):
        search_term = f"%{q}%"
        query = query.filter(
            db.or_(
                Attraction.name.ilike(search_term),
                Attraction.description.ilike(search_term)
            )
        )
    if province := request.args.get('province'):
        query = query.filter(Attraction.province.ilike(f"%{province}%"))
    if category := request.args.get('category'):
        query = query.filter(Attraction.category.ilike(f"%{category}%"))

    paginated_attractions = query.order_by(Attraction.name).paginate(page=page, per_page=limit, error_out=False)
    results = [attraction.to_dict() for attraction in paginated_attractions.items]

    pagination_data = {
        'total_pages': paginated_attractions.pages,
        'current_page': paginated_attractions.page,
        'total_items': paginated_attractions.total,
        'has_next': paginated_attractions.has_next,
        'has_prev': paginated_attractions.has_prev
    }

    return standardized_response(data={'attractions': results, 'pagination': pagination_data}, message="Attractions retrieved successfully.")

@attractions_bp.route('/attractions/<int:attraction_id>', methods=['GET'])
def get_attraction_detail(attraction_id):
    attraction = Attraction.query.get_or_404(attraction_id, description="Attraction not found.")
    return standardized_response(data=attraction.to_dict(), message="Attraction retrieved successfully.")

@attractions_bp.route('/attractions', methods=['POST'])
@jwt_required()
def add_attraction():
    if 'cover_image' not in request.files:
        abort(400, description="Missing 'cover_image' in request.")

    file = request.files['cover_image']
    if file.filename == '':
        abort(400, description="No selected file.")

    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join('uploads', filename)
        file.save(upload_path)

        data = request.form
        if not all(k in data for k in ('name', 'description', 'province', 'category')):
            abort(400, description="Missing required fields.")
        try:
            new_attraction = Attraction(
                name=data.get('name'),
                description=data.get('description'),
                address=data.get('address'),
                province=data.get('province'),
                district=data.get('district'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                category=data.get('category'),
                opening_hours=data.get('opening_hours'),
                entrance_fee=data.get('entrance_fee'),
                contact_phone=data.get('contact_phone'),
                website=data.get('website'),
                main_image_url=filename,
                image_urls=data.get('image_urls')
            )
            db.session.add(new_attraction)
            db.session.commit()
            return standardized_response(data={'id': new_attraction.id}, message="Attraction added successfully.", status_code=201)
        except Exception:
            db.session.rollback()
            abort(500, description="Failed to add attraction.")

@attractions_bp.route('/attractions/<int:attraction_id>', methods=['PUT'])
@jwt_required()
def update_attraction(attraction_id):
    attraction = Attraction.query.get_or_404(attraction_id, description="Attraction not found.")
    data = request.get_json()
    if not data:
        abort(400, description="Request body cannot be empty.")

    try:
        for key, value in data.items():
            if hasattr(attraction, key):
                setattr(attraction, key, value)
        db.session.commit()
        return standardized_response(data=attraction.to_dict(), message="Attraction updated successfully.")
    except Exception:
        db.session.rollback()
        abort(500, description="Failed to update attraction.")

@attractions_bp.route('/attractions/<int:attraction_id>', methods=['DELETE'])
@jwt_required()
def delete_attraction(attraction_id):
    attraction = Attraction.query.get_or_404(attraction_id, description="Attraction not found.")
    try:
        db.session.delete(attraction)
        db.session.commit()
        return standardized_response(message="Attraction deleted successfully.")
    except Exception:
        db.session.rollback()
        abort(500, description="Failed to delete attraction.")
