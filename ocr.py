import sys
import json

from ocr_core import run_ocr


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Image path is required."}))
        return

    result = run_ocr(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
