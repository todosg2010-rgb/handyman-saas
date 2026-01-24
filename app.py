import os
from flask import Flask, request, jsonify, send_file
from pricing_engine import изчисли_оферта

app = Flask(__name__)
app.json.ensure_ascii = False  # Bulgarian characters support


# =========================
# PAGE ROUTES
# =========================

@app.route("/")
def landing():
    return send_file("index.html")


@app.route("/demo")
def demo():
    return send_file("demo.html")


# Bulgarian-friendly route + English alias (both work)
@app.route("/kak-raboti")
@app.route("/how-it-works")
def kak_raboti():
    return send_file("how-it-works.html")


# =========================
# IMAGE ROUTE (NO /static)
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
# API ROUTE
# =========================

@app.route("/api/izchisli", methods=["POST"])
def izchisli():
    data = request.get_json()

    if not data:
        return jsonify({"грешка": "Няма подадени данни"}), 400

    required_fields = ["описание", "трудност", "часове", "разстояние", "материали"]
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

