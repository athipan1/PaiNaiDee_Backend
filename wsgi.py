import os
from flask_api import FlaskAPI
from flask import send_from_directory
from src.app import create_app

# กำหนด path ของ static (React build)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# ใช้ create_app() ของคุณ แต่เปลี่ยน base class เป็น FlaskAPI
# สมมติว่า create_app() คืนค่า Flask instance ปกติ
# เราสามารถ wrap ให้เป็น FlaskAPI ได้
flask_app = create_app(os.environ.get("FLASK_ENV", "production"))
app = FlaskAPI(
    flask_app.import_name,
    static_folder=STATIC_DIR,
    static_url_path="/"
)
app.config.update(flask_app.config)
app.register_blueprint(flask_app.blueprints['api']) if 'api' in flask_app.blueprints else None

# ===== Serve React Frontend =====
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """
    ถ้า path เป็นไฟล์ static ที่มีอยู่ → ส่งไฟล์นั้น
    ถ้าไม่ใช่ → ส่ง index.html ของ React
    """
    target_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(target_path):
        return send_from_directory(app.static_folder, path)
    else:
        index_file = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(app.static_folder, "index.html")
        else:
            return {
                "data": None,
                "message": "React build not found. Run `npm run build` in the frontend directory.",
                "success": True
            }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
