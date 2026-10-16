
"""Ventana principal de Screen Extractor."""

from PIL import Image
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QHBoxLayout,
)

from screen_extractor.capture.kwin_capture import KWinCapture
from screen_extractor.services.clipboard_service import ClipboardService
from screen_extractor.services.ocr_service import OCRService
from screen_extractor.ui.region_selector import RegionSelector


class MainWindow(QMainWindow):
    """Interfaz para capturar una región y extraer su texto."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Screen Extractor")
        self.resize(760, 560)
        self.setMinimumSize(600, 440)

        # especificar Icono
        self.setWindowIcon(QIcon.fromTheme("accessories-text-editor"))

        # Los servicios se mantienen separados de la interfaz.
        self.capture_service = KWinCapture()
        self.ocr_service = OCRService()
        self.clipboard_service = ClipboardService()

        self._build_ui()
        self._load_languages()

    def _build_ui(self) -> None:
        """Construye y organiza los controles de la ventana."""

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(12)

        self.title_label = QLabel("Screen Extractor")
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)

        self.description_label = QLabel(
            "Selecciona una región de la pantalla para extraer "
            "su texto mediante reconocimiento óptico de caracteres."
        )
        self.description_label.setObjectName("descriptionLabel")
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        layout.addSpacing(8)

        self.language_label = QLabel("Idioma de reconocimiento")
        self.language_label.setObjectName("sectionLabel")
        layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.setMinimumHeight(38)
        self.language_combo.setAccessibleName(
            "Idioma de reconocimiento"
        )
        layout.addWidget(self.language_combo)

        self.capture_button = QPushButton("Capturar y extraer texto")
        self.capture_button.setObjectName("primaryButton")
        self.capture_button.setMinimumHeight(42)
        self.capture_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.capture_button.clicked.connect(self.extract_from_screen)
        layout.addWidget(self.capture_button)

        layout.addSpacing(8)

        self.result_label = QLabel("Texto reconocido")
        self.result_label.setObjectName("sectionLabel")
        layout.addWidget(self.result_label)

        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText(
            "El texto extraído aparecerá aquí..."
        )
        self.result_text.setAcceptRichText(False)
        self.result_text.setAccessibleName("Texto reconocido")
        self.result_text.setMinimumHeight(180)
        layout.addWidget(self.result_text, 1)

                # Acciones del resultado en una sola fila.
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        self.copy_button = QPushButton("Copiar texto")
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.setMinimumHeight(38)
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_result)
        actions_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("Guardar como TXT")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.setMinimumHeight(38)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_result)
        actions_layout.addWidget(self.save_button)

        self.clear_button = QPushButton("Limpiar resultado")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.setMinimumHeight(38)
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear_result)
        actions_layout.addWidget(self.clear_button)

        layout.addLayout(actions_layout)


        self.status_label = QLabel("Listo para capturar.")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(24)
        layout.addWidget(self.status_label)

        self.setCentralWidget(central_widget)


        self.setStyleSheet("""
            QMainWindow {
                background-color: palette(window);
                color: palette(window-text);
            }

            QWidget {
                color: palette(window-text);
                font-size: 13px;
            }

            QLabel#titleLabel {
                font-size: 25px;
                font-weight: 700;
            }

            QLabel#descriptionLabel,
            QLabel#statusLabel {
                color: palette(placeholder-text);
            }

            QLabel#sectionLabel {
                font-size: 13px;
                font-weight: 600;
            }

            QComboBox {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 7px;
                padding: 6px 10px;
            }

            QComboBox QAbstractItemView {
                background-color: palette(base);
                color: palette(text);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }

            QPushButton {
                background-color: palette(button);
                color: palette(button-text);
                border: 1px solid palette(mid);
                border-radius: 7px;
                padding: 8px 14px;
                font-weight: 600;
            }

            QPushButton:hover:enabled {
                border-color: palette(highlight);
            }

            QPushButton:pressed:enabled {
                background-color: palette(midlight);
            }

            QPushButton:disabled {
                color: palette(mid);
            }

            QPushButton#primaryButton {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: 1px solid palette(highlight);
            }

            QTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 7px;
                padding: 10px;
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }

            QComboBox:focus,
            QTextEdit:focus {
                border: 1px solid palette(highlight);
            }
        """)

    
    def _load_languages(self) -> None:
        """Carga los idiomas disponibles según Tesseract."""

        try:
            languages = self.ocr_service.get_available_languages()

            for label, language_code in languages:
                self.language_combo.addItem(label, language_code)

            if not languages:
                self.capture_button.setEnabled(False)
                self.status_label.setText(
                    "No se encontraron idiomas de Tesseract."
                )

        except Exception as exc:
            self.capture_button.setEnabled(False)
            self.status_label.setText(
                "No se pudieron cargar los idiomas."
            )
            QMessageBox.critical(
                self,
                "Error al cargar idiomas",
                f"No se pudieron consultar los idiomas de Tesseract.\n\n{exc}",
            )

    def extract_from_screen(self) -> None:
        """Ejecuta el flujo completo de captura, selección y OCR."""

        language = self.language_combo.currentData()

        if not language:
            QMessageBox.warning(
                self,
                "Idioma no disponible",
                "Selecciona un idioma válido para el reconocimiento.",
            )
            return

        self.capture_button.setEnabled(False)
        self.status_label.setText("Capturando pantalla...")

        try:
            capture_path = self.capture_service.capture()

            with Image.open(capture_path) as screenshot:
                screenshot.load()

                selector = RegionSelector(str(capture_path))
                selection_result = selector.exec()

                if selection_result != QDialog.DialogCode.Accepted:
                    self.status_label.setText("Selección cancelada.")
                    return

                region: QRect | None = selector.selected_region

                if region is None:
                    self.status_label.setText(
                        "No se seleccionó una región."
                    )
                    return

                cropped_image = screenshot.crop(
                    (
                        region.x(),
                        region.y(),
                        region.x() + region.width(),
                        region.y() + region.height(),
                    )
                )

            self.status_label.setText("Reconociendo texto...")

            text = self.ocr_service.extract_text(
                cropped_image,
                language,
            )

            self.result_text.setPlainText(text)
            has_text = bool(text.strip())

            self.copy_button.setEnabled(has_text)
            self.save_button.setEnabled(has_text)
            self.clear_button.setEnabled(has_text)

            if text.strip():
                self.status_label.setText(
                    f"Reconocimiento completado: "
                    f"{len(text.strip())} caracteres."
                )
            else:
                self.status_label.setText(
                    "No se reconoció texto en la región seleccionada."
                )

        except Exception as exc:
            self.status_label.setText("Ocurrió un error durante la extracción.")
            QMessageBox.critical(
                self,
                "Error durante la extracción",
                str(exc),
            )

        finally:
            self.capture_button.setEnabled(True)

    def copy_result(self) -> None:
        """Copia el resultado actual al portapapeles."""

        text = self.result_text.toPlainText()

        if not text.strip():
            return

        try:
            self.clipboard_service.copy(text)
            self.status_label.setText(
                f"Texto copiado al portapapeles "
                f"({len(text.strip())} caracteres)."
            )

        except Exception as exc:
            self.status_label.setText(
                "No se pudo copiar el texto al portapapeles."
            )
            QMessageBox.critical(
                self,
                "Error al copiar",
                str(exc),
            )


    def clear_result(self) -> None:
        """Limpia el texto reconocido y actualiza el estado."""

        if not self.result_text.toPlainText():
            return

        self.result_text.clear()
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.status_label.setText("Resultado limpiado. Listo para capturar.")



    def save_result(self) -> None:
        """Guarda el texto reconocido en un archivo TXT."""

        text = self.result_text.toPlainText()

        if not text.strip():
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar texto reconocido",
            "texto_reconocido.txt",
            "Archivos de texto (*.txt)",
        )

        # Si el usuario cancela el diálogo, no hacemos nada.
        if not file_path:
            return

        if not file_path.lower().endswith(".txt"):
            file_path += ".txt"

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)

            self.status_label.setText(
                f"Texto guardado en: {file_path}"
            )

        except OSError as exc:
            QMessageBox.critical(
                self,
                "Error al guardar",
                f"No se pudo guardar el archivo.\n\n{exc}",
            )
            self.status_label.setText(
                "No se pudo guardar el texto."
            )
