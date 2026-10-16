
from pathlib import Path
from collections import defaultdict

import pytesseract
from pytesseract import Output
from PIL import Image

CAPTURE = Path.home() / "capture.png"
OUTPUT = Path.home() / "ocr-structured.txt"


def main():
    if not CAPTURE.is_file():
        print(f"No existe la captura: {CAPTURE}")
        return

    with Image.open(CAPTURE) as source:
        image = source.convert("RGB")

    data = pytesseract.image_to_data(
        image,
        lang="spa+eng",
        config="--psm 6",
        output_type=Output.DICT,
    )

    # Agrupar palabras por bloque, párrafo y línea.
    lines = defaultdict(list)
    line_positions = {}

    count = len(data["text"])

    for i in range(count):
        word = data["text"][i].strip()

        if not word:
            continue

        try:
            confidence = float(data["conf"][i])
        except (ValueError, TypeError):
            continue

        # Ignorar detecciones con confianza muy baja.
        if confidence < 25:
            continue

        key = (
            data["block_num"][i],
            data["par_num"][i],
            data["line_num"][i],
        )

        lines[key].append({
            "text": word,
            "left": data["left"][i],
        })

        line_positions[key] = {
            "block": data["block_num"][i],
            "paragraph": data["par_num"][i],
            "top": data["top"][i],
            "height": data["height"][i],
        }

    output_lines = []
    previous_block = None
    previous_paragraph = None
    previous_bottom = None

    # Ordenar por posición vertical y luego horizontal.
    ordered_keys = sorted(
        lines.keys(),
        key=lambda key: (
            line_positions[key]["top"],
            line_positions[key]["block"],
            line_positions[key]["paragraph"],
        ),
    )

    for key in ordered_keys:
        words = sorted(lines[key], key=lambda word: word["left"])
        text = " ".join(word["text"] for word in words)

        position = line_positions[key]
        current_block = position["block"]
        current_paragraph = position["paragraph"]
        current_top = position["top"]

        if output_lines:
            new_block = current_block != previous_block
            new_paragraph = (
                current_block == previous_block
                and current_paragraph != previous_paragraph
            )

            if new_block or new_paragraph:
                output_lines.append("")
            elif (
                previous_bottom is not None
                and current_top - previous_bottom > 1.5 * position["height"]
            ):
                # Separación visual grande: posible párrafo nuevo.
                output_lines.append("")

        output_lines.append(text)

        previous_block = current_block
        previous_paragraph = current_paragraph
        previous_bottom = position["top"] + position["height"]

    result = "\n".join(output_lines).strip()
    OUTPUT.write_text(result + "\n", encoding="utf-8")

    print("========== TEXTO ESTRUCTURADO ==========")
    print(result or "[No se detectó texto]")
    print("=========================================")
    print(f"\nResultado guardado en: {OUTPUT}")


if __name__ == "__main__":
    main()
