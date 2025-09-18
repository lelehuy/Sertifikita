#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ELECTRON_DIR="$ROOT/electron"
DIST_PY="$ROOT/dist-python"
ICON="$ELECTRON_DIR/build/icon.icns"
DMG_BG="$ELECTRON_DIR/build/dmg-background.png"

echo "▶️  Build DMG (Electron + electron-builder)"
echo "    ROOT         : $ROOT"
echo "    ELECTRON_DIR : $ELECTRON_DIR"
echo

# 1) pastikan Python .app sudah dibangun
"$ROOT/scripts/build_py.sh"

if [[ ! -d "$DIST_PY/Sertifikita.app" ]]; then
  echo "❌ $DIST_PY/Sertifikita.app tidak ditemukan."
  exit 1
fi

# 2) cek aset optional
[[ -f "$ICON"   ]] || echo "⚠️  Peringatan: $ICON tidak ditemukan. (Electron akan pakai ikon default)"
[[ -f "$DMG_BG" ]] || echo "⚠️  Peringatan: $DMG_BG tidak ditemukan. (DMG pakai background default)"

# 3) install deps electron
if ! command -v npm >/dev/null 2>&1; then
  echo "❌ npm tidak ditemukan. Install Node.js dulu."
  exit 1
fi

echo
echo "📦 Install deps Electron..."
cd "$ELECTRON_DIR"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi

# 4) build DMG
echo
echo "🛠  electron-builder → DMG ..."
npm run dist

# 5) output info
echo
echo "📦 Output DMG:"
ls -1t "$ELECTRON_DIR/dist"/*.dmg 2>/dev/null || echo "⚠️  Tidak menemukan file .dmg di electron/dist"

