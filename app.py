import os
from flask import Flask, request, jsonify, send_file
from pricing_engine import изчисли_оферта

app = Flask(__name__)
app.json.ensure_ascii = False  # Bulgarian UTF-8 support


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
# STATIC IMAGE
# =========================

@app.route("/ui-preview.png")
def ui_preview():
    return send_file("ui-preview.png", mimetype="image/png")


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# =========================
# API ROUTE
# =========================

@app.route("/api/izchisli", methods=["POST"])
def izchisli():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"грешка": "Няма подадени данни"}), 400

    # Required for Engine v1
    required_fields = ["описание", "часове", "разстояние", "материали"]
    for field in required_fields:
        if field not in data:
            return jsonify({"грешка": f"Липсва поле: {field}"}), 400

    try:
        result = изчисли_оферта(data)
        return jsonify(result), 200
    except Exception as e:
        # Fail safe for demo
        return jsonify({"грешка": "Вътрешна грешка"}), 500


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)

