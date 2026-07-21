# Python OCR Service

Standalone HTTP service exposing the project's existing PaddleOCR logic
(previously invoked as a Node.js subprocess) as a single endpoint, so it
can be deployed on Render as its own service, independent of the Node.js
API.

The OCR logic itself (`ocr_core.py`) is unchanged from the original
`backend/python/ocr.py` script — it was only restructured from a
CLI script into a plain function (`run_ocr(image_path)`) so it can be
called from an HTTP request handler instead of `sys.argv`.

## Files

- `ocr_core.py` — the OCR logic: loads PaddleOCR once at import time,
  normalizes the input image (HEIC/HEIF → JPEG via Pillow), runs OCR, and
  returns `{ success, text, lines }` / `{ success: false, error }`.
- `app.py` — Flask app exposing `POST /api/ocr/process` and `GET /health`.
- `ocr.py` — optional CLI entry point for local/manual testing, same
  interface as the original script (`python ocr.py path/to/image.jpg`).
- `requirements.txt` — OCR dependencies (unchanged versions) plus
  `flask` + `gunicorn` for the HTTP layer.

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env
python app.py        # dev server, listens on PORT (default 5001)
```

## Run in production

```bash
gunicorn --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT app:app
```

Use a single worker: PaddleOCR's model is loaded once per worker process,
and each additional worker duplicates that memory cost.

## API

### `POST /api/ocr/process`

`multipart/form-data` with a single field `image`.

Success (`200`):
```json
{ "success": true, "text": "line one\nline two", "lines": ["line one", "line two"] }
```

Failure (`400`/`500`):
```json
{ "success": false, "error": "message" }
```

### `GET /health`

```json
{ "success": true, "status": "ok" }
```

See `../RENDER_DEPLOYMENT.md` for full Render deployment steps for this
service alongside the Node.js backend.
