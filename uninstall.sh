#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/opt/yg-screen-extractor"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/local/share/applications"

run_root() {
    if [[ "$EUID" -eq 0 ]]; then
        "$@"
    else
        sudo "$@"
    fi
}

printf 'Se desinstalará YG Screen Extractor y sus componentes instalados.\n'
printf 'No se eliminarán paquetes del sistema, capturas ni atajos personales.\n\n'

read -r -p '¿Deseas continuar? [s/N] ' answer

case "$answer" in
    s|S|si|SI|Si|sí|Sí|SÍ)
        ;;
    *)
        printf 'Desinstalación cancelada.\n'
        exit 0
        ;;
esac

run_root rm -f \
    "$BIN_DIR/yg-screen-extractor" \
    "$BIN_DIR/yg-screen-extractor-capture-helper" \
    "$DESKTOP_DIR/yg-screen-extractor.desktop" \
    "$DESKTOP_DIR/io.github.screenocr.capture-helper.desktop"

run_root rm -rf "$APP_DIR"

if command -v update-desktop-database >/dev/null 2>&1; then
    run_root update-desktop-database "$DESKTOP_DIR" || true
fi

printf '\nYG Screen Extractor se ha retirado del sistema.\n'
printf 'Las dependencias del sistema y los datos personales se han conservado.\n'
