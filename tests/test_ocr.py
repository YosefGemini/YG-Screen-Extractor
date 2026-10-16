
import subprocess
import sys
from pathlib import Path

import pytesseract
from PIL import Image

HELPER = Path("/usr/local/bin/screen-ocr-capture-helper")
CAPTURE = Path.home() / "capture.png"

def main() -> int:
    print("=== Prueba de integración Python + C++ + Tesseract ===")

    if not HELPER.is_file():
        print(f"ERROR: no existe el helper: {HELPER}")
        return 1

    # Generar una captura nueva.
    try:
        result = subprocess.run(
            [str(HELPER)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR al ejecutar el helper: {exc}")
        return 2

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        print(f"ERROR: helper finalizó con código {result.returncode}")
        return 3

    if not CAPTURE.is_file():
        print(f"ERROR: no se encontró la captura: {CAPTURE}")
        return 4

    # Abrir y validar la imagen con Pillow.
    try:
        with Image.open(CAPTURE) as source:
            source.verify()

        with Image.open(CAPTURE) as source:
            image = source.convert("RGB")
            print(f"[OK] Imagen: {image.width} x {image.height}")
    except Exception as exc:
        print(f"ERROR al abrir la imagen: {exc}")
        return 5

    # Comprobar que Tesseract reconoce los idiomas configurados.
    try:
        languages = set(pytesseract.get_languages(config=""))
    except pytesseract.TesseractNotFoundError:
        print("ERROR: no se encuentra el ejecutable de Tesseract.")
        return 6

    print(f"Idiomas instalados: {', '.join(sorted(languages))}")

    selected_languages = [
        language
        for language in ("spa", "eng")
        if language in languages
    ]

    if not selected_languages:
        print("ERROR: no está instalado spa ni eng.")
        return 7

    language_argument = "+".join(selected_languages)
    print(f"Ejecutando OCR con: {language_argument}")

    try:
        text = pytesseract.image_to_string(
            image,
            lang=language_argument,
        ).strip()
    except pytesseract.TesseractError as exc:
        print(f"ERROR durante el OCR: {exc}")
        return 8

    print("\n========== TEXTO EXTRAÍDO ==========")
    print(text if text else "[No se detectó texto]")
    print("====================================")

    output = Path.home() / "ocr-result.txt"
    output.write_text(text + "\n", encoding="utf-8")

    print(f"\n[OK] Resultado guardado en: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
