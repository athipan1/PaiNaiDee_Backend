from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import json

load_dotenv()  # โหลดค่าจากไฟล์ .env

app = Flask(__name__)
CORS(app)

# --- การตั้งค่า Database ---
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
def fetch_data_from_database():
    path = os.path.join(os.path.dirname(__file__), "attractions_cleaned_from_api.json")
    with open(path, encoding="utf-8-sig") as f:  # ✅ ใช้ utf-8-sig เพื่อข้าม BOM
        return json.load(f)

@app.route("/api/attractions", methods=["GET"])
def get_attractions():
    try:
        data = fetch_data_from_database()
        response = make_response(jsonify(data))
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/ping-db")
def ping_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM attractions;")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"status": "✅ Connected", "rows": count})
    except Exception as e:
        return jsonify({"status": "❌ Failed", "error": str(e)}), 500
# --- API ---
@app.route('/')
def home():
    return jsonify(message="Welcome to Pai Nai Dii Backend!")

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
        return jsonify(results)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="Failed to fetch data"), 500
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
            return jsonify(data)
        return jsonify(message="Not found"), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="Error getting detail"), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/attractions', methods=['POST'])
def add_attraction():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify(message="Missing 'name'"), 400

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
        return jsonify(message="Added", id=new_id), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(error="Insert failed"), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
