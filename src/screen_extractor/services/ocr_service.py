
"""Servicio responsable de reconocer texto mediante Tesseract OCR."""

from pathlib import Path

import pytesseract
from PIL import Image

from screen_extractor.config import DEFAULT_LANGUAGES, OCR_CONFIG


class OCRService:
    """Encapsula las operaciones de reconocimiento óptico de caracteres."""

    def get_available_languages(self) -> list[tuple[str, str]]:
        """
        Devuelve las opciones de idioma disponibles en Tesseract.

        Las opciones principales solo se incluyen cuando sus datos de idioma
        están instalados. 'osd' se omite porque detecta orientación y no es
        un idioma de reconocimiento de texto.
        """
        installed = set(pytesseract.get_languages(config=""))
        options: list[tuple[str, str]] = []

        for label, language_code in DEFAULT_LANGUAGES.items():
            required_languages = set(language_code.split("+"))

            if required_languages.issubset(installed):
                options.append((label, language_code))

        # Añade otros idiomas instalados que no estén entre las opciones
        # principales. Así se puede ampliar la aplicación sin modificar
        # este servicio cada vez que se instale un idioma nuevo.
        known_codes = set(DEFAULT_LANGUAGES.values())

        for language_code in sorted(installed):
            if language_code == "osd" or language_code in known_codes:
                continue

            options.append((language_code, language_code))

        return options

    def extract_text(
        self,
        image: Image.Image | str | Path,
        language: str,
    ) -> str:
        """
        Reconoce el texto de una imagen.

        Se conserva PSM 6 como configuración predeterminada para mantener
        el comportamiento validado en el prototipo.
        """
        if isinstance(image, (str, Path)):
            with Image.open(image) as opened_image:
                return pytesseract.image_to_string(
                    opened_image,
                    lang=language,
                    config=OCR_CONFIG,
                )

        return pytesseract.image_to_string(
            image,
            lang=language,
            config=OCR_CONFIG,
        )
