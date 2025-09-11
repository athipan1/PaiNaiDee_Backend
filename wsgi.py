import os
from flask import Flask, send_from_directory
from src.app import create_app

# กำหนด path ของ static (React build)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# ใช้ create_app() ของคุณ
flask_app = create_app(os.environ.get("FLASK_ENV", "production"))

# ✅ ใช้ Flask ปกติ ไม่ต้อง FlaskAPI
app = Flask(
    flask_app.import_name,
    static_folder=STATIC_DIR,
    static_url_path="/"
)

# รวม config เดิม
app.config.update(flask_app.config)

# ✅ Register blueprint ถ้ามี api
if "api" in flask_app.blueprints:
    app.register_blueprint(flask_app.blueprints["api"])


# ===== Serve React Frontend =====
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """
    ถ้า path เป็นไฟล์ static ที่มีอยู่ → ส่งไฟล์นั้น
    ถ้าไม่ใช่ → ส่ง index.html ของ React
    """
    target_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(target_path):
        return send_from_directory(app.static_folder, path)

    index_file = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_file):
        return send_from_directory(app.static_folder, "index.html")

    return {
        "data": None,
        "message": "React build not found. Run `npm run build` in the frontend directory.",
        "success": False,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)