import os
import tempfile

from PIL import Image
from pillow_heif import register_heif_opener
from paddleocr import PaddleOCR

# HEIC / HEIF support
register_heif_opener()

# Load model only once, at import time (module-level, same as the
# original script) so a single worker process pays the model-load cost
# once and reuses it across every request.
ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)


def prepare_image(image_path):
    """
    Convert any supported image format into a temporary JPEG
    so PaddleOCR receives a standard image.
    """

    if not os.path.exists(image_path):
        raise Exception(f"Image not found: {image_path}")

    image = Image.open(image_path)

    # Convert RGBA / P / LA etc. to RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    temp_path = temp_file.name
    temp_file.close()

    image.save(
        temp_path,
        "JPEG",
        quality=95
    )

    return temp_path


def run_ocr(image_path):
    """
    Runs OCR on the given image path and returns the same result shape
    that was previously printed to stdout by the CLI script:
      {"success": True, "text": "...", "lines": [...]}
      {"success": False, "error": "..."}
    """

    temp_path = None

    try:
        temp_path = prepare_image(image_path)

        results = ocr.predict(temp_path)

        lines = []

        for result in results:

            if not isinstance(result, dict):
                continue

            for text in result.get("rec_texts", []):

                text = str(text).strip()

                if text:
                    lines.append(text)

        unique_lines = list(dict.fromkeys(lines))

        return {
            "success": True,
            "text": "\n".join(unique_lines),
            "lines": unique_lines,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
