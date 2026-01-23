from flask import Flask, request, jsonify, send_file
from pricing_engine import изчисли_оферта
import os

app = Flask(__name__)
app.json.ensure_ascii = False


# =========================
# UI ROUTES
# =========================

@app.route("/", methods=["GET"])
def landing_page():
    return send_file("index.html")


@app.route("/demo", methods=["GET"])
def demo_page():
    return send_file("demo.html")


# =========================
# IMAGE ROUTE (NO static/)
# =========================

@app.route("/ui-preview.png", methods=["GET"])
def ui_preview():
    return send_file("ui-preview.png")


# =========================
# API ROUTES
# =========================

@app.route("/api/изчисли", methods=["POST"])
def api_izchisli():
    данни = request.get_json()

    if not данни:
        return jsonify({"грешка": "Липсва JSON тяло"}), 400

    задължителни = ["описание", "трудност", "часове", "разстояние", "материали"]
    for поле in задължителни:
        if поле not in данни:
            return jsonify({"грешка": f"Липсва поле: {поле}"}), 400

    try:
        резултат = изчисли_оферта(данни)
        return jsonify(резултат), 200
    except Exception as e:
        return jsonify({
            "грешка": "Грешка при изчисление",
            "детайли": str(e)
        }), 500

@app.route("/dashboard")
def dashboard():
    return send_from_directory(
        os.path.dirname(__file__),
        "dashboard.html"
    )


# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

