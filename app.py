import os
from flask import Flask, request, jsonify, send_file
from pricing_engine import изчисли_оферта

app = Flask(__name__)
app.json.ensure_ascii = False  # allow Bulgarian characters

# ---------- PAGES ----------

@app.route("/")
def landing_page():
    return send_file("index.html")

@app.route("/demo")
def demo_page():
    return send_file("demo.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ---------- API ----------

@app.route("/api/izchisli", methods=["POST"])
def izchisli():
    data = request.get_json()

    if not data:
        return jsonify({"greshka": "Няма подадени данни"}), 400

    # Normalize Bulgarian keys → Latin
    mapping = {
        "описание": "описание",
        "трудност": "трудност",
        "часове": "часове",
        "разстояние": "разстояние",
        "материали": "материали"
    }

    normalized = {}
    for k, v in data.items():
        normalized[mapping.get(k, k)] = v

    required = ["описание", "трудност", "часове", "разстояние", "материали"]
    for field in required:
        if field not in normalized:
            return jsonify({"грешка": f"Липсва поле: {field}"}), 400

    try:
        result = изчисли_оферта(normalized)
        return jsonify(result)
    except Exception as e:
        return jsonify({"грешка": str(e)}), 500


# ---------- RUN ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)

