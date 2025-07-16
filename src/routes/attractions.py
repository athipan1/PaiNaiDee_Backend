import json
from flask import Blueprint, jsonify, request
from ..models import Attraction, db

attractions_bp = Blueprint('attractions', __name__)

@attractions_bp.route('/attractions', methods=['GET'])
def get_attractions():
    try:
        query = Attraction.query

        # Search by name or description
        q = request.args.get('q')
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                db.or_(
                    Attraction.name.ilike(search_term),
                    Attraction.description.ilike(search_term)
                )
            )

        # Filter by province
        province = request.args.get('province')
        if province:
            query = query.filter(Attraction.province.ilike(f"%{province}%"))

        # Filter by category
        category = request.args.get('category')
        if category:
            query = query.filter(Attraction.category.ilike(f"%{category}%"))

        attractions = query.all()

        attraction_list = []
        for attraction in attractions:
            # Safely load image_urls JSON
            try:
                image_urls = json.loads(attraction.image_urls) if attraction.image_urls else []
            except (json.JSONDecodeError, TypeError):
                image_urls = []

            attraction_list.append({
                'id': attraction.id,
                'name': attraction.name,
                'description': attraction.description,
                'latitude': attraction.latitude,
                'longitude': attraction.longitude,
                'province': attraction.province,
                'category': attraction.category,
                'image_urls': image_urls
            })

        return jsonify(attraction_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attractions_bp.route('/attractions', methods=['POST'])
def add_attraction():
    try:
        data = request.get_json()

        # Basic validation
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400

        # Convert image_urls list to JSON string
        image_urls = data.get('image_urls', [])
        if isinstance(image_urls, list):
            image_urls_json = json.dumps(image_urls)
        else:
            # Handle cases where image_urls is not a list (e.g., already a string)
            image_urls_json = image_urls

        new_attraction = Attraction(
            name=data['name'],
            description=data.get('description', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            province=data.get('province', ''),
            category=data.get('category', ''),
            image_urls=image_urls_json
        )

        db.session.add(new_attraction)
        db.session.commit()

        return jsonify({'message': 'Attraction added successfully', 'id': new_attraction.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
