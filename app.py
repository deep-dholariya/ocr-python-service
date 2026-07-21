import os
import tempfile

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from ocr_core import run_ocr

app = Flask(__name__)

# Mirrors the Node service's MAX_FILE_SIZE (bytes).
app.config["MAX_CONTENT_LENGTH"] = int(
    os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024)
)


@app.get("/health")
def health():
    """Liveness/readiness probe."""
    return jsonify({"success": True, "status": "ok"}), 200


@app.post("/api/ocr/process")
def process_ocr():
    """
    Request:
        multipart/form-data
        field name = image

    Response:
        {
            "success": true,
            "text": "...",
            "lines": []
        }
    """

    if "image" not in request.files:
        return jsonify(
            {
                "success": False,
                "error": "Image file is required."
            }
        ), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify(
            {
                "success": False,
                "error": "Image file is required."
            }
        ), 400

    filename = secure_filename(file.filename) or "upload"
    suffix = os.path.splitext(filename)[1] or ".jpg"

    tmp = tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False
    )

    tmp_path = tmp.name
    tmp.close()

    try:
        print("=" * 50)
        print("1. Request received")

        file.save(tmp_path)

        print("2. File saved:")
        print(tmp_path)

        print("3. Calling run_ocr()")

        result = run_ocr(tmp_path)

        print("4. OCR completed")

        print("5. Result:")
        print(result)

        status_code = 200 if result.get("success") else 500

        return jsonify(result), status_code

    except Exception as e:
        print("APP.PY ERROR:")
        print(str(e))

        return jsonify(
            {
                "success": False,
                "error": str(e)
            }
        ), 500

    finally:
        print("6. Cleaning temporary file")

        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        print("=" * 50)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))

    app.run(
        host="0.0.0.0",
        port=port
    )