from flask import Blueprint, jsonify
from ..models import Attraction

attractions_bp = Blueprint('attractions', __name__)

@attractions_bp.route('/attractions')
def get_attractions():
    attractions = [
        {'id': 1, 'name': 'Wat Arun', 'description': 'Temple of Dawn'},
        {'id': 2, 'name': 'Grand Palace', 'description': 'The official residence of the Kings of Siam'},
    ]
    return jsonify(attractions)
