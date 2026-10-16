"""Gestión del portapapeles en Wayland."""

import shutil
import subprocess


class ClipboardService:
    """Copia texto al portapapeles sin depender de la vida de Qt."""

    def copy(self, text: str) -> None:
        wl_copy = shutil.which("wl-copy")

        if wl_copy is None:
            raise RuntimeError(
                "No se encontró wl-copy. Instala el paquete "
                "'wl-clipboard' para copiar texto en Wayland."
            )

        try:
            subprocess.run(
                [wl_copy, "--type", "text/plain"],
                input=text,
                text=True,
                check=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Se agotó el tiempo al copiar al portapapeles."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "No se pudo copiar el texto al portapapeles."
            ) from exc