from flask import Blueprint, jsonify, request, make_response
from src.models import db, Attraction

attractions_bp = Blueprint('attractions', __name__)

@attractions_bp.route('/attractions', methods=['GET'])
def get_all_attractions():
    try:
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

        attractions = query.order_by(Attraction.name).all()
        results = [attraction.to_dict() for attraction in attractions]

        response = make_response(jsonify(results))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        print(f"Error: {e}")
        response = make_response(jsonify(error="Failed to fetch data"), 500)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

@attractions_bp.route('/attractions/<int:attraction_id>', methods=['GET'])
def get_attraction_detail(attraction_id):
    try:
        attraction = Attraction.query.get(attraction_id)
        if attraction:
            response = make_response(jsonify(attraction.to_dict()))
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response
        response = make_response(jsonify(message="Not found"), 404)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        print(f"Error: {e}")
        response = make_response(jsonify(error="Error getting detail"), 500)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

@attractions_bp.route('/attractions', methods=['POST'])
def add_attraction():
    data = request.get_json()
    if not data or 'name' not in data:
        response = make_response(jsonify(message="Missing 'name'"), 400)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

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
            main_image_url=data.get('main_image_url'),
            image_urls=data.get('image_urls')
        )
        db.session.add(new_attraction)
        db.session.commit()
        response = make_response(jsonify(message="Added", id=new_attraction.id), 201)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        response = make_response(jsonify(error="Insert failed"), 500)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
