from flask import Flask, request, jsonify, send_file

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


@app.route("/kak-raboti", methods=["GET"])
def how_it_works_page():
    return send_file("how-it-works.html")


@app.route("/ui-preview.png", methods=["GET"])
def ui_preview():
    return send_file("ui-preview.png")


# =========================
# API ROUTE
# =========================

@app.route("/api/izchisli", methods=["POST"])
def api_izchisli():
    try:
        raw_data = request.get_json(force=True)

        # ---- Normalize Bulgarian -> internal keys ----
        key_map = {
            "описание": "описание",
            "трудност": "трудност",
            "часове": "часове",
            "разстояние": "разстояние",
            "материали": "материали"
        }

        data = {}
        for k, v in raw_data.items():
            data[key_map.get(k, k)] = v

        # ---- Validate required fields ----
        required_fields = ["описание", "трудност", "часове", "разстояние", "материали"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "грешка": f"Липсва поле: {field}"
                }), 400

        if not isinstance(data["материали"], list):
            data["материали"] = []

        # ---- Call pricing engine ----
        from pricing_engine import изчисли_оферта
        result = изчисли_оферта(data)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "грешка": "Вътрешна грешка в сървъра",
            "детайли": str(e)
        }), 500


# =========================
# HEALTH CHECK
# =========================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# =========================
# LOCAL DEV ONLY
# =========================
# Gunicorn ignores this on Render

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5050,
        debug=True
    )

