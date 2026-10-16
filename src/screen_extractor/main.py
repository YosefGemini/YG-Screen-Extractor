

"""Punto de entrada de Screen Extractor."""

import argparse

from screen_extractor.app import main, quick_capture


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrae texto de una región de la pantalla."
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Ejecuta la captura rápida, copia el texto y cierra.",
    )

    args = parser.parse_args()

    if args.quick:
        raise SystemExit(quick_capture())

    raise SystemExit(main())
