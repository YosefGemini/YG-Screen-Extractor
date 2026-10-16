"""Inicialización y ciclo de vida de la aplicación Qt."""

import subprocess
import sys

from PIL import Image
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from screen_extractor.capture.kwin_capture import KWinCapture
from screen_extractor.services.clipboard_service import ClipboardService
from screen_extractor.services.ocr_service import OCRService
from screen_extractor.ui.main_window import MainWindow
from screen_extractor.ui.region_selector import RegionSelector


def create_application() -> QApplication:
    """Obtiene la instancia de Qt o crea una nueva."""
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("Screen Extractor")
    app.setOrganizationName("Screen Extractor")

    return app


def main() -> int:
    """Muestra la ventana principal y ejecuta el bucle de eventos."""
    app = create_application()

    window = MainWindow()
    window.show()

    return app.exec()




def quick_capture() -> int:
    """Captura una región, reconoce texto y lo copia al portapapeles."""
    app = create_application()

    capture_service = KWinCapture()
    ocr_service = OCRService()
    clipboard_service = ClipboardService()

    language = "spa+eng"

    def execute_capture() -> None:
        try:
            # Consultar directamente a KWin qué salida está activa
            # bajo el cursor, sin depender de QCursor.pos().
            result = subprocess.run(
                [
                    "qdbus6",
                    "org.kde.KWin",
                    "/KWin",
                    "org.kde.KWin.activeOutputName",
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )

            screen_name = result.stdout.strip()

            if not screen_name:
                raise RuntimeError(
                    "KWin no devolvió el nombre del monitor."
                )

            available_screens = {
                screen.name()
                for screen in QApplication.screens()
            }

            print(
                f"[Screen Extractor] Monitor detectado por KWin: "
                f"{screen_name!r}",
                flush=True,
            )

            if screen_name not in available_screens:
                raise RuntimeError(
                    f"KWin identificó el monitor {screen_name!r}, "
                    "pero Qt no lo encuentra entre las pantallas "
                    f"disponibles: {sorted(available_screens)}"
                )

            # Capturar el monitor correcto con el helper validado.
            capture_path = capture_service.capture(screen_name)

            # Mostrar el selector en ese mismo monitor.
            selector = RegionSelector(
                str(capture_path),
                screen_name=screen_name,
            )

            if selector.exec() != QDialog.DialogCode.Accepted:
                return

            region = selector.selected_region

            if region is None:
                return

            # Recortar la región seleccionada.
            with Image.open(capture_path) as screenshot:
                screenshot.load()

                cropped_image = screenshot.crop(
                    (
                        region.x(),
                        region.y(),
                        region.x() + region.width(),
                        region.y() + region.height(),
                    )
                )

            # Reconocer el texto.
            text = ocr_service.extract_text(
                cropped_image,
                language,
            )

            if not text.strip():
                print(
                    "[Screen Extractor] No se detectó texto.",
                    flush=True,
                )
                return

            # wl-copy conserva el portapapeles tras cerrar Python.
            clipboard_service.copy(text)

            print(
                f"[Screen Extractor] Texto copiado: "
                f"{len(text.strip())} caracteres.",
                flush=True,
            )

        except subprocess.CalledProcessError as exc:
            details = exc.stderr.strip() or exc.stdout.strip()

            print(
                f"[Screen Extractor] Error consultando KWin: "
                f"{details or exc}",
                file=sys.stderr,
                flush=True,
            )

            QMessageBox.critical(
                None,
                "Screen Extractor",
                "No se pudo consultar el monitor activo en KWin.",
            )

        except Exception as exc:
            print(
                f"[Screen Extractor] Error: {exc}",
                file=sys.stderr,
                flush=True,
            )

            QMessageBox.critical(
                None,
                "Screen Extractor",
                f"No se pudo completar la captura:\n\n{exc}",
            )

        finally:
            app.quit()

    QTimer.singleShot(0, execute_capture)

    return app.exec()
