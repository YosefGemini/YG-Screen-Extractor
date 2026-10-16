
import struct
import subprocess
import sys
from pathlib import Path

HELPER = Path("/usr/local/bin/screen-ocr-capture-helper")
CAPTURE = Path.home() / "capture.png"


def main() -> int:
    print("=== Prueba de integración Python + C++ ===")

    # 1. Comprobar que el helper está instalado y es ejecutable.
    if not HELPER.is_file():
        print(f"ERROR: no existe el helper: {HELPER}")
        return 1

    if not HELPER.stat().st_mode & 0o111:
        print(f"ERROR: el helper no tiene permisos de ejecución: {HELPER}")
        return 1

    print(f"[OK] Helper encontrado: {HELPER}")

    # 2. Ejecutar el helper como usuario normal.
    print("\nSolicitando captura...")

    try:
        result = subprocess.run(
            [str(HELPER)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: el helper superó el límite de 30 segundos.")
        return 2
    except OSError as exc:
        print(f"ERROR al ejecutar el helper: {exc}")
        return 2

    if result.stdout:
        print("Salida del helper:")
        print(result.stdout.strip())

    if result.stderr:
        print("Errores del helper:")
        print(result.stderr.strip())

    if result.returncode != 0:
        print(f"ERROR: el helper terminó con código {result.returncode}.")
        return 3

    print("[OK] El helper terminó correctamente.")

    # 3. Verificar que la captura existe y es un PNG válido.
    if not CAPTURE.is_file():
        print(f"ERROR: no se generó la captura: {CAPTURE}")
        return 4

    try:
        with CAPTURE.open("rb") as image_file:
            header = image_file.read(24)
    except OSError as exc:
        print(f"ERROR al leer la captura: {exc}")
        return 4

    png_signature = b"\x89PNG\r\n\x1a\n"

    if len(header) < 24 or header[:8] != png_signature:
        print("ERROR: el archivo generado no tiene una cabecera PNG válida.")
        return 5

    if header[12:16] != b"IHDR":
        print("ERROR: el PNG no contiene un encabezado IHDR válido.")
        return 5

    width, height = struct.unpack(">II", header[16:24])

    if width == 0 or height == 0:
        print("ERROR: las dimensiones de la captura no son válidas.")
        return 5

    print(f"[OK] Captura PNG válida: {CAPTURE}")
    print(f"[OK] Resolución: {width} x {height}")
    print(f"[OK] Tamaño: {CAPTURE.stat().st_size:,} bytes")

    print("\nRESULTADO: integración Python + helper C++ correcta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
