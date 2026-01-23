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
def kak_raboti_page():
    return send_file("how-it-works.html")


@app.route("/ui-preview.png", methods=["GET"])
def ui_preview():
    return send_file("ui-preview.png")


# =========================
# API ROUTES
# =========================

@app.route("/api/izchisli", methods=["POST"])
def api_izchisli():
    data = request.get_json()

    if not data:
        return jsonify({"greshka": "Lipsva JSON tyalo"}), 400

    required = ["opisanie", "trudnost", "chasove", "razstoyanie", "materiali"]
    for field in required:
        if field not in data:
            return jsonify({"greshka": f"Lipsva pole: {field}"}), 400

    try:
        from pricing_engine import izchisli_oferta
        result = izchisli_oferta(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "greshka": "Greshka pri izchislenie",
            "detayli": str(e)
        }), 500


# =========================
# RENDER ENTRY POINT
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )

