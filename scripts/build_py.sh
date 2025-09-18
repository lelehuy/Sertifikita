#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT/app"
DIST_PY="$ROOT/dist-python"
WORK_PY="$ROOT/build-py"
SPEC="$ROOT/Sertifikita.spec"

PY="${ROOT}/.venv/bin/python"
PIP="${ROOT}/.venv/bin/pip"

echo "▶️  Build Python app (Sertifikita) ..."
cd "$ROOT"

"$PIP" install -r "$APP_DIR/requirements.txt"

rm -rf "$WORK_PY" "$DIST_PY"
mkdir -p "$DIST_PY"

"$PY" -m PyInstaller \
  --clean --noconfirm \
  --distpath "$DIST_PY" \
  --workpath "$WORK_PY" \
  "$SPEC"

echo "✅ Selesai. Hasil: $DIST_PY/Sertifikita.app"
