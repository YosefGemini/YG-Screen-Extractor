
"""Configuración central de la aplicación Screen Extractor."""

from pathlib import Path

# Ejecutable nativo que solicita la captura a KWin mediante D-Bus.
CAPTURE_HELPER = Path(
    "/usr/local/bin/yg-screen-extractor-capture-helper"
)
# El helper C++ guarda la captura en esta ruta.
CAPTURE_PATH = Path.home() / "capture.png"

# Configuración de Tesseract:
# PSM 6 asume un bloque de texto uniforme y funciona bien para este caso.
OCR_CONFIG = "--psm 6"

# Idiomas principales que ofrecerá la interfaz.
DEFAULT_LANGUAGES = {
    "Español": "spa",
    "English": "eng",
    "Español + English": "spa+eng",
}
