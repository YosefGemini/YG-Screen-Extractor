from pathlib import Path

import pytesseract
from PIL import Image

CAPTURE = Path.home() / "capture.png"
OUTPUT_DIR = Path.home() / "ocr-modes"

def main():
    if not CAPTURE.is_file():
        print(f"No existe la captura: {CAPTURE}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with Image.open(CAPTURE) as source:
        image = source.convert("RGB")

    for psm in (3, 6, 11):
        print(f"\n{'=' * 20} PSM {psm} {'=' * 20}")

        text = pytesseract.image_to_string(
            image,
            lang="spa+eng",
            config=f"--psm {psm}",
        ).strip()

        print(text or "[No se detectó texto]")

        output = OUTPUT_DIR / f"psm-{psm}.txt"
        output.write_text(text + "\n", encoding="utf-8")
        print(f"\nGuardado en: {output}")

if __name__ == "__main__":
    main()