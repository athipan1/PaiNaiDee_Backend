from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import config
import os
import json

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    CORS(app)
    return app

config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

def get_db_connection():
    return psycopg2.connect(
        host=app.config["DB_HOST"],
        database=app.config["DB_NAME"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        port=app.config["DB_PORT"]
    )

# --- API ---
@app.route('/')
def home():
    response = make_response(jsonify(message="Welcome to Pai Nai Dii Backend!"))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/attractions', methods=['GET'])
def get_all_attractions():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT * FROM attractions"
        filters = []
        params = []

        # รองรับการค้นหา
        if q := request.args.get('q'):
            filters.append("(name ILIKE %s OR description ILIKE %s)")
            params.extend([f"%{q}%", f"%{q}%"])
        if province := request.args.get('province'):
            filters.append("province ILIKE %s")
            params.append(f"%{province}%")
        if category := request.args.get('category'):
            filters.append("category ILIKE %s")
            params.append(f"%{category}%")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY name"

        cur.execute(query, tuple(params))
        results = cur.fetchall()
        response = make_response(jsonify(results))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        print(f"Error: {e}")
        response = make_response(jsonify(error="Failed to fetch data"), 500)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/attractions/<int:attraction_id>', methods=['GET'])
def get_attraction_detail(attraction_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM attractions WHERE id = %s", (attraction_id,))
        data = cur.fetchone()
        if data:
            response = make_response(jsonify(data))
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
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/attractions', methods=['POST'])
def add_attraction():
    data = request.get_json()
    if not data or 'name' not in data:
        response = make_response(jsonify(message="Missing 'name'"), 400)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    try:
        # แปลง image_urls ให้เป็น string JSON ถ้ายังเป็น list อยู่
        image_urls = data.get('image_urls')
        if isinstance(image_urls, list):
            image_urls = json.dumps(image_urls)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO attractions (
                name, description, address, province, district,
                latitude, longitude, category, opening_hours,
                entrance_fee, contact_phone, website,
                main_image_url, image_urls
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            data.get('name'), data.get('description'), data.get('address'),
            data.get('province'), data.get('district'), data.get('latitude'),
            data.get('longitude'), data.get('category'), data.get('opening_hours'),
            data.get('entrance_fee'), data.get('contact_phone'), data.get('website'),
            data.get('main_image_url'), image_urls
        ))
        new_id = cur.fetchone()[0]
        conn.commit()
        response = make_response(jsonify(message="Added", id=new_id), 201)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        print(f"Error: {e}")
        response = make_response(jsonify(error="Insert failed"), 500)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
