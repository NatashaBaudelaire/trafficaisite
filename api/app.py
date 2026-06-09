"""API Flask do TrafficAI — serve o front-end e expõe inferência de severidade."""

from __future__ import annotations

import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from predictor import get_model_info, predict_accident

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "front-end"

app = Flask(__name__, static_folder=None)
CORS(app)


@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.route("/<path:filename>")
def static_files(filename: str):
    if filename.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(FRONTEND, filename)


@app.route("/api/health", methods=["GET"])
def health():
    info = get_model_info()
    return jsonify({"status": "ok", **info})


@app.route("/api/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    description = (payload.get("description") or "").strip()
    image_provided = bool(payload.get("image"))
    fields = payload.get("fields") or {}

    if not description and not image_provided and not fields:
        return jsonify({"error": "Informe uma descrição, dados contextuais ou envie uma imagem."}), 400

    start = time.perf_counter()
    result = predict_accident(
        description=description,
        image_provided=image_provided,
        fields=fields,
    )
    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

    return jsonify(
        {
            **result,
            "analysis_time": f"{elapsed_ms / 1000:.1f}s",
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
