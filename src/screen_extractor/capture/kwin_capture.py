"""Captura de pantalla mediante el helper nativo de KWin."""

import subprocess
from pathlib import Path

from screen_extractor.config import CAPTURE_HELPER, CAPTURE_PATH


class KWinCapture:
    """Coordina la ejecución del helper C++ y valida su resultado."""

    def __init__(
        self,
        helper_path: Path = CAPTURE_HELPER,
        capture_path: Path = CAPTURE_PATH,
    ) -> None:
        self.helper_path = helper_path
        self.capture_path = capture_path

    def capture(self, screen_name: str | None = None) -> Path:
        """Captura el monitor indicado o la pantalla activa."""

        if not self.helper_path.is_file():
            raise FileNotFoundError(
                f"No se encontró el helper: {self.helper_path}"
            )

        self.capture_path.parent.mkdir(parents=True, exist_ok=True)

        if self.capture_path.exists():
            self.capture_path.unlink()

        command = [str(self.helper_path)]

        if screen_name:
            command.append(screen_name)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "La captura excedió el tiempo máximo de espera."
            ) from exc

        if result.returncode != 0:
            details = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"Falló la captura de KWin: {details}")

        if not self.capture_path.is_file():
            raise RuntimeError("No se generó la imagen de captura.")

        if self.capture_path.stat().st_size == 0:
            raise RuntimeError("La imagen de captura está vacía.")

        return self.capture_path