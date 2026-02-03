import os
from flask import Flask, request, jsonify, send_file

# -------------------------
# Flask + DB
# -------------------------
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# -------------------------
# Business logic
# -------------------------
from pricing_engine import изчисли_оферта

# -------------------------
# App setup
# -------------------------
app = Flask(__name__)
app.json.ensure_ascii = False  # Bulgarian UTF-8 support

# -------------------------
# Database config
# -------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///local.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# IMPORTANT: load models so Flask-Migrate sees them
import models  # noqa: E402


# =========================
# PAGE ROUTES
# =========================

@app.route("/")
def landing():
    return send_file("index.html")


@app.route("/demo")
def demo():
    return send_file("demo.html")


# Bulgarian + English routes
@app.route("/kak-raboti")
@app.route("/how-it-works")
def kak_raboti():
    return send_file("how-it-works.html")


# =========================
# IMAGE ROUTE (NO STATIC)
# =========================

@app.route("/ui-preview.png")
def ui_preview():
    return send_file("ui-preview.png", mimetype="image/png")


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# =========================
# API: PRICING ENGINE
# =========================

@app.route("/api/izchisli", methods=["POST"])
def izchisli():
    data = request.get_json()

    if not data:
        return jsonify({"грешка": "Няма подадени данни"}), 400

    required_fields = ["описание", "часове", "разстояние", "материали"]
    for field in required_fields:
        if field not in data:
            return jsonify({"грешка": f"Липсва поле: {field}"}), 400

    try:
        result = изчисли_оферта(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"грешка": str(e)}), 500


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
