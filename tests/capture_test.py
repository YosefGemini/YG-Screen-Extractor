
import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtDBus import (
    QDBusConnection,
    QDBusMessage,
    QDBusPendingCallWatcher,
    QDBusUnixFileDescriptor,
)
from PySide6.QtGui import QImage


SERVICE = "org.kde.KWin.ScreenShot2"
OBJECT_PATH = "/org/kde/KWin/ScreenShot2"
INTERFACE = "org.kde.KWin.ScreenShot2"

OUTPUT = Path.home() / "dev" / "screen-ocr-poc" / "capture.png"


def unwrap(value):
    """Desenvuelve QDBusVariant si Qt lo devuelve explícitamente."""
    if hasattr(value, "variant"):
        return value.variant()
    return value


def capture_active_screen(app: QCoreApplication):
    connection = QDBusConnection.sessionBus()

    if not connection.isConnected():
        print("ERROR: no hay conexión al bus D-Bus de sesión.")
        app.exit(1)
        return

    read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
    dbus_fd = None

    try:
        # QDBusUnixFileDescriptor conserva su propio descriptor.
        dbus_fd = QDBusUnixFileDescriptor(write_fd)

        message = QDBusMessage.createMethodCall(
            SERVICE,
            OBJECT_PATH,
            INTERFACE,
            "CaptureActiveScreen",
        )

        message.setArguments([
            {
                "include-cursor": False,
                "native-resolution": True,
            },
            dbus_fd,
        ])

        # El descriptor original ya no es necesario.
        os.close(write_fd)
        write_fd = -1

        print("Solicitando captura de la pantalla activa a KWin...")

        pending = connection.asyncCall(message, 60000)
        watcher = QDBusPendingCallWatcher(pending, app)

        def on_finished():
            nonlocal dbus_fd

            try:
                reply = watcher.reply()

                if reply.type() == QDBusMessage.MessageType.ErrorMessage:
                    print("ERROR D-Bus:", reply.errorMessage())
                    print("Nombre del error:", reply.errorName())
                    app.exit(2)
                    return

                arguments = reply.arguments()
                if not arguments:
                    raise RuntimeError(
                        "KWin devolvió una respuesta sin metadatos."
                    )

                metadata = {
                    key: unwrap(value)
                    for key, value in dict(arguments[0]).items()
                }

                print("Metadatos:", metadata)

                if metadata.get("type") != "raw":
                    raise RuntimeError(
                        f"Formato de captura inesperado: "
                        f"{metadata.get('type')!r}"
                    )

                width = int(metadata["width"])
                height = int(metadata["height"])
                pixel_format = QImage.Format(
                    int(metadata["format"])
                )

                if width <= 0 or height <= 0:
                    raise RuntimeError("Dimensiones de imagen inválidas.")

                image = QImage(width, height, pixel_format)
                if image.isNull():
                    raise RuntimeError(
                        "Qt no pudo crear la imagen con ese formato."
                    )

                expected = image.sizeInBytes()

                # Cerramos nuestra copia del descriptor de escritura.
                # KWin conserva la suya mientras transmite la imagen.
                if dbus_fd is not None:
                    dbus_fd.close()
                    dbus_fd = None

                data = bytearray()

                while len(data) < expected:
                    chunk = os.read(
                        read_fd,
                        min(1024 * 1024, expected - len(data)),
                    )
                    if not chunk:
                        break
                    data.extend(chunk)

                if len(data) != expected:
                    raise RuntimeError(
                        f"Imagen incompleta: {len(data)} bytes recibidos; "
                        f"se esperaban {expected}."
                    )

                image.bits()[:expected] = data

                OUTPUT.parent.mkdir(parents=True, exist_ok=True)

                if not image.save(str(OUTPUT), "PNG"):
                    raise RuntimeError(
                        f"No se pudo guardar la imagen en {OUTPUT}"
                    )

                print(f"Captura guardada correctamente: {OUTPUT}")
                print(f"Dimensiones: {width} x {height}")
                app.exit(0)

            except Exception as exc:
                print(f"ERROR procesando la captura: {exc}")
                app.exit(3)

            finally:
                watcher.deleteLater()

        watcher.finished.connect(on_finished)

    except Exception:
        if dbus_fd is not None:
            dbus_fd.close()
        raise

    finally:
        if write_fd >= 0:
            os.close(write_fd)

        # read_fd debe permanecer abierto hasta finalizar la lectura.
        # Se cierra al salir del bucle de eventos.
        app.aboutToQuit.connect(
            lambda: os.close(read_fd)
            if read_fd >= 0
            else None
        )


def main():
    app = QCoreApplication(sys.argv)

    try:
        capture_active_screen(app)
    except Exception as exc:
        print(f"ERROR inicializando la captura: {exc}")
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
