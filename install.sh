
#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="YG Screen Extractor"
APP_DIR="/opt/yg-screen-extractor"
BIN_DIR="/usr/local/bin"
APP_LAUNCHER="$BIN_DIR/yg-screen-extractor"
HELPER="$BIN_DIR/yg-screen-extractor-capture-helper"
DESKTOP_DIR="/usr/local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/yg-screen-extractor.desktop"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$BUILD_DIR"
}
trap cleanup EXIT

run_root() {
    if [[ "$EUID" -eq 0 ]]; then
        "$@"
    else
        sudo "$@"
    fi
}

fail() {
    printf '\nERROR: %s\n' "$*" >&2
    exit 1
}

printf '\n=== Instalador de %s ===\n' "$APP_NAME"

# Comprobar los archivos fuente requeridos.
for file in \
    "$SCRIPT_DIR/src/screen_extractor/main.py" \
    "$SCRIPT_DIR/src/screen_extractor/config.py" \
    "$SCRIPT_DIR/capture-helper/CMakeLists.txt" \
    "$SCRIPT_DIR/capture-helper/main.cpp" \
    "$SCRIPT_DIR/requirements.txt" \
    "$SCRIPT_DIR/packaging/yg-screen-extractor-launcher.sh" \
    "$SCRIPT_DIR/packaging/screen-extractor.desktop"
do
    [[ -f "$file" ]] || fail "No se encontró el archivo requerido: $file"
done

# Comprobar la distribución.
[[ -r /etc/os-release ]] || fail "No se pudo identificar la distribución Linux."
source /etc/os-release

case " ${ID:-} ${ID_LIKE:-} " in
    *arch*|*garuda*)
        ;;
    *)
        fail "Esta versión del instalador admite Arch Linux y derivados. Sistema detectado: ${PRETTY_NAME:-desconocido}"
        ;;
esac

command -v pacman >/dev/null 2>&1 ||
    fail "No se encontró pacman."

if [[ "$EUID" -ne 0 ]]; then
    command -v sudo >/dev/null 2>&1 ||
        fail "Instala sudo o ejecuta el instalador como root."
fi

printf '\n[1/7] Instalando dependencias del sistema...\n'

PACKAGES=(
    base-devel
    cmake
    qt6-base
    qt6-tools
    python
    python-pip
    tesseract
    wl-clipboard
)

run_root pacman -S --needed "${PACKAGES[@]}"

command -v qdbus6 >/dev/null 2>&1 ||
    fail "No se encontró qdbus6 después de instalar qt6-tools."

command -v tesseract >/dev/null 2>&1 ||
    fail "Tesseract no está disponible."

command -v wl-copy >/dev/null 2>&1 ||
    fail "wl-copy no está disponible."

ensure_tesseract_language() {
    local language="$1"
    local package="$2"
    local traineddata="/usr/share/tessdata/${language}.traineddata"

    if tesseract --list-langs 2>/dev/null | grep -qx "$language"; then
        printf 'Idioma disponible: %s\n' "$language"
        return 0
    fi

    if [[ -e "$traineddata" ]]; then
        fail "Existe $traineddata, pero Tesseract no reconoce '$language'. Revisa el archivo antes de continuar."
    fi

    printf 'Instalando idioma requerido: %s\n' "$language"
    run_root pacman -S --needed "$package"

    if ! tesseract --list-langs 2>/dev/null | grep -qx "$language"; then
        fail "Tesseract no reconoce el idioma '$language' después de instalar $package."
    fi
}

ensure_tesseract_language eng tesseract-data-eng
ensure_tesseract_language spa tesseract-data-spa

printf '\nIdiomas base de Tesseract verificados correctamente.\n'

# qdbus6 es necesario para consultar el monitor activo en KWin.
command -v qdbus6 >/dev/null 2>&1 ||
    fail "No se encontró qdbus6 después de instalar qt6-tools."

command -v tesseract >/dev/null 2>&1 ||
    fail "Tesseract no está disponible."

command -v wl-copy >/dev/null 2>&1 ||
    fail "wl-copy no está disponible."

printf '\n[2/7] Verificando idiomas de Tesseract...\n'

LANGUAGES="$(tesseract --list-langs 2>/dev/null)"

for language in eng spa; do
    if ! grep -qx "$language" <<< "$LANGUAGES"; then
        fail "Tesseract no tiene el idioma '$language'. Revisa los paquetes de datos instalados."
    fi
done

printf '\n[3/7] Preparando la instalación en %s...\n' "$APP_DIR"

run_root install -d "$APP_DIR/src" "$DESKTOP_DIR"

# Reemplazar únicamente el código de esta aplicación instalada.
run_root rm -rf "$APP_DIR/src/screen_extractor"
run_root cp -a \
    "$SCRIPT_DIR/src/screen_extractor" \
    "$APP_DIR/src/screen_extractor"

run_root install -m 644 \
    "$SCRIPT_DIR/requirements.txt" \
    "$APP_DIR/requirements.txt"

# Evitar instalar cachés generadas durante el desarrollo.
run_root find "$APP_DIR/src/screen_extractor" \
    -type d -name __pycache__ -prune -exec rm -rf {} +

run_root find "$APP_DIR/src/screen_extractor" \
    -type f -name '*.pyc' -delete

printf '\n[4/7] Creando el entorno Python e instalando dependencias...\n'

if [[ ! -x "$APP_DIR/venv/bin/python" ]]; then
    run_root python -m venv "$APP_DIR/venv"
fi

run_root "$APP_DIR/venv/bin/python" -m pip install \
    --upgrade pip

run_root "$APP_DIR/venv/bin/python" -m pip install \
    -r "$APP_DIR/requirements.txt"

printf '\n[5/7] Compilando e instalando el helper C++...\n'

cmake -S "$SCRIPT_DIR/capture-helper" \
    -B "$BUILD_DIR" \
    -DCMAKE_INSTALL_PREFIX=/usr/local

cmake --build "$BUILD_DIR" --parallel

run_root cmake --install "$BUILD_DIR"

printf '\n[6/7] Instalando los lanzadores...\n'

run_root install -Dm755 \
    "$SCRIPT_DIR/packaging/yg-screen-extractor-launcher.sh" \
    "$APP_LAUNCHER"

run_root install -Dm644 \
    "$SCRIPT_DIR/packaging/screen-extractor.desktop" \
    "$DESKTOP_FILE"

printf '\n[7/7] Verificando la instalación...\n'

[[ -x "$APP_LAUNCHER" ]] ||
    fail "No se instaló el lanzador de la aplicación."

[[ -x "$HELPER" ]] ||
    fail "No se instaló el helper C++."

[[ -x "$APP_DIR/venv/bin/python" ]] ||
    fail "No se encontró el intérprete del entorno virtual."

run_root "$APP_DIR/venv/bin/python" -m compileall -q \
    "$APP_DIR/src/screen_extractor" ||
    fail "Falló la comprobación de sintaxis Python."

run_root "$APP_DIR/venv/bin/python" -c \
    'import PySide6, PIL, pytesseract' ||
    fail "No se pudieron importar las dependencias Python."

if command -v update-desktop-database >/dev/null 2>&1; then
    run_root update-desktop-database "$DESKTOP_DIR" || true
fi

printf '\nInstalación completada correctamente.\n'
printf 'Aplicación: %s\n' "$APP_LAUNCHER"
printf 'Captura rápida: %s --quick\n' "$APP_LAUNCHER"
printf 'Directorio: %s\n' "$APP_DIR"
printf '\nLa captura seguirá guardándose en ~/capture.png.\n'
printf 'Las dependencias instaladas por pacman no se eliminarán al desinstalar la aplicación.\n'
