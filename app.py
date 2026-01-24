import os
from flask import Flask, request, jsonify, send_file
from pricing_engine import изчисли_оферта

app = Flask(__name__)
app.json.ensure_ascii = False


# ---------- PAGES ----------

@app.route("/")
def landing():
    return send_file("index.html")


@app.route("/demo")
def demo():
    return send_file("demo.html")


@app.route("/how-it-works")
def how_it_works():
    return send_file("how-it-works.html")


# ---------- IMAGE (NO STATIC FOLDER) ----------

@app.route("/ui-preview.png")
def ui_image():
    return send_file("ui-preview.png", mimetype="image/png")


# ---------- HEALTH ----------

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ---------- API ----------

@app.route("/api/izchisli", methods=["POST"])
def izchisli():
    data = request.get_json()

    if not data:
        return jsonify({"грешка": "Няма подадени данни"}), 400

    required = ["описание", "трудност", "часове", "разстояние", "материали"]
    for field in required:
        if field not in data:
            return jsonify({"грешка": f"Липсва поле: {field}"}), 400

    try:
        result = изчисли_оферта(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"грешка": str(e)}), 500


# ---------- RUN ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)

