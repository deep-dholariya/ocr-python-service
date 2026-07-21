import os
import tempfile

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from ocr_core import run_ocr

app = Flask(__name__)

# Mirrors the Node service's MAX_FILE_SIZE (bytes). Rejects oversized
# uploads before they're fully buffered.
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))


@app.get("/health")
def health():
    """Liveness/readiness probe for Render."""
    return jsonify({"success": True, "status": "ok"}), 200


@app.post("/api/ocr/process")
def process_ocr():
    """
    Single OCR endpoint.

    Request:  multipart/form-data, field name "image"
    Response: same JSON shape the previous CLI script printed to stdout:
        200 {"success": true, "text": "...", "lines": [...]}
        4xx/5xx {"success": false, "error": "..."}
    """
    if "image" not in request.files or request.files["image"].filename == "":
        return jsonify({"success": False, "error": "Image file is required."}), 400

    file = request.files["image"]
    filename = secure_filename(file.filename) or "upload"
    suffix = os.path.splitext(filename)[1] or ".jpg"

    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        file.save(tmp_path)
        result = run_ocr(tmp_path)
        status_code = 200 if result.get("success") else 500
        return jsonify(result), status_code
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
