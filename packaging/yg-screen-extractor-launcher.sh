#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/yg-screen-extractor"

export PYTHONPATH="$APP_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$APP_DIR/venv/bin/python" \
    -m screen_extractor.main \
    "$@"
