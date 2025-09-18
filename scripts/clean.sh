#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT/app"
ELECTRON_DIR="$ROOT/electron"

DEEP=0
if [[ "${1:-}" == "--deep" || "${1:-}" == "-d" ]]; then
  DEEP=1
fi

echo "🧹 Clean artifacts"
echo "   ROOT: $ROOT"
echo

# Python build artifacts
rm -rf "$APP_DIR/build" "$APP_DIR/dist"
find "$APP_DIR" -name "__pycache__" -type d -prune -exec rm -rf {} +
find "$APP_DIR" -name "*.pyc" -delete

# Bundle staging
rm -rf "$ROOT/dist-python"

# Electron build artifacts
rm -rf "$ELECTRON_DIR/dist"
# (jangan hapus build/ karena ada icon/icns & dmg-background)
# rm -rf "$ELECTRON_DIR/build"   # <- kalau mau, uncomment (hati-hati aset hilang)

if [[ $DEEP -eq 1 ]]; then
  echo "⚠️  Deep clean (node_modules & venv)"
  rm -rf "$ELECTRON_DIR/node_modules"
  rm -rf "$ROOT/.venv"
fi

echo "✅ Clean done."

