
"""Selector visual de una región rectangular de la captura."""

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QCursor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QDialog


class RegionSelector(QDialog):
    """Permite seleccionar una zona de la imagen mediante el ratón."""

    def __init__(
    self,
    image_path: str,
    screen_name: str | None = None,
) -> None:
        super().__init__()

        self.setWindowTitle("Selecciona una región")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.pixmap = QPixmap(image_path)

        if self.pixmap.isNull():
            raise ValueError(
                f"No se pudo cargar la captura: {image_path}"
            )

        # La selección se expresa en coordenadas de la imagen original.
        self.selected_region: QRect | None = None

        self._start_point: QPoint | None = None
        self._current_point: QPoint | None = None
        self._selecting = False

        # Sitúa el selector en el monitor donde está el cursor.
        # Esto resulta útil en escritorios con varias pantallas.
        # Preferir el monitor seleccionado para la captura.
                # Preferir el monitor que corresponde a la captura.
        screen = next(
            (
                candidate
                for candidate in QApplication.screens()
                if screen_name
                and candidate.name() == screen_name
            ),
            None,
        )

        if screen is None:
            screen = QApplication.screenAt(QCursor.pos())

        if screen is None:
            screen = QApplication.primaryScreen()

        if screen is not None:
            # Crear el identificador de ventana para obtener su handle.
            self.winId()

            handle = self.windowHandle()

            if handle is not None:
                handle.setScreen(screen)

            self.setGeometry(screen.geometry())

            print(
                f"[RegionSelector] Monitor: {screen.name()!r}; "
                f"geometría: {screen.geometry()}",
                flush=True,
            )

        self.setWindowState(Qt.WindowState.WindowFullScreen)

    # def showEvent(self, event) -> None:
    #     """Muestra el selector a pantalla completa."""
    #     super().showEvent(event)
    #     self.showFullScreen()


        # FIN INIT

    def paintEvent(self, event) -> None:
        """Dibuja la captura y la superposición de selección."""
        painter = QPainter(self)

        # La imagen ocupa el selector completo. Después convertiremos
        # la selección visual a las coordenadas de la imagen original.
        painter.drawPixmap(self.rect(), self.pixmap)

        if self._selecting and self._start_point and self._current_point:
            selection = QRect(
                self._start_point,
                self._current_point,
            ).normalized()

            # Oscurece el área seleccionada para que destaque el rectángulo.
            painter.fillRect(
                selection,
                QColor(40, 120, 255, 45),
            )

            painter.setPen(
                QPen(
                    QColor(40, 120, 255),
                    2,
                    Qt.PenStyle.SolidLine,
                )
            )
            painter.drawRect(selection)

    def mousePressEvent(self, event) -> None:
        """Inicia la selección con el botón izquierdo."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_point = event.position().toPoint()
            self._current_point = self._start_point
            self._selecting = True
            self.update()

    def mouseMoveEvent(self, event) -> None:
        """Actualiza el rectángulo mientras se mueve el ratón."""
        if self._selecting:
            self._current_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        """Convierte la selección visual a coordenadas originales."""
        if (
            event.button() != Qt.MouseButton.LeftButton
            or not self._selecting
            or self._start_point is None
        ):
            return

        self._current_point = event.position().toPoint()
        self._selecting = False

        selected = QRect(
            self._start_point,
            self._current_point,
        ).normalized()

        if selected.width() < 2 or selected.height() < 2:
            self.update()
            return

        # El selector puede tener dimensiones distintas a las de la
        # captura; cada eje se escala de forma independiente.
        scale_x = self.pixmap.width() / self.width()
        scale_y = self.pixmap.height() / self.height()

        x = round(selected.x() * scale_x)
        y = round(selected.y() * scale_y)
        width = round(selected.width() * scale_x)
        height = round(selected.height() * scale_y)

        # Limita el rectángulo para no salir de los límites de la imagen.
        x = max(0, min(x, self.pixmap.width() - 1))
        y = max(0, min(y, self.pixmap.height() - 1))
        width = max(1, min(width, self.pixmap.width() - x))
        height = max(1, min(height, self.pixmap.height() - y))

        self.selected_region = QRect(x, y, width, height)
        self.accept()

    def keyPressEvent(self, event) -> None:
        """Permite cancelar la selección con Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.selected_region = None
            self.reject()
            return

        super().keyPressEvent(event)
