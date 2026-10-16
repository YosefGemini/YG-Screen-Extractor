# Changelog

Todos los cambios relevantes de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/lang/es/).

## [Sin publicar]

## [0.1.0-alpha] - 2026-10-16

Primer **MVP (Producto Mínimo Viable)** del proyecto. Versión **alpha**:
funcional para el flujo principal en KDE Plasma 6 (KWin / Wayland), pero con
API y comportamiento todavía sujetos a cambios.

### Añadido

- Captura de pantalla en KDE Plasma mediante la API D-Bus
  `org.kde.KWin.ScreenShot2`.
- Helper nativo en **C++/Qt6** (`yg-screen-extractor-capture-helper`) que
  solicita la captura a KWin y la guarda en `~/capture.png`.
- Interfaz gráfica con **Qt6 / PySide6** para capturar y extraer texto.
- Selector visual de región con soporte para múltiples monitores.
- Reconocimiento de texto con **Tesseract OCR**.
- Idiomas `spa`, `eng` y `spa+eng` con detección automática de los datos de
  idioma instalados.
- Copia del texto al portapapeles en Wayland mediante `wl-copy`.
- Guardado del texto reconocido como archivo **TXT**.
- Modo rápido `--quick` para atajos de teclado globales en Plasma.
- Lanzador e integración con el menú de aplicaciones mediante archivo
  `.desktop`.
- Instalador (`install.sh`) y desinstalador (`uninstall.sh`) para Arch Linux y
  derivadas.
- Pruebas manuales de integración de captura y OCR en `tests/`.

### Conocido

- La integración automática de atajos desde la aplicación aún no está
  implementada (`src/screen_extractor/shortcuts/kde_shortcut.py` es un
  marcador de posición); los atajos se configuran manualmente en Plasma.
- Solo se admiten Arch Linux y sus derivadas.
- Requiere una sesión KDE Plasma con KWin sobre Wayland.

[Sin publicar]: https://github.com/YosefGemini/YG-Screen-Extractor/commits/main
[0.1.0-alpha]: https://github.com/YosefGemini/YG-Screen-Extractor/releases/tag/v0.1.0-alpha
