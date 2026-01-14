# Sertifikita - Developer Documentation

This document contains technical information for developers who want to contribute to Sertifikita or build it from source.

## 🛠️ Development Setup

### Prerequisites
- Python 3.10 – 3.13
- Node.js & NPM (only for building the DMG)

### Local Environment
```bash
# 1) Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r app/requirements.txt

# 3) Launch developer UI
python app/main.py
```

## 🏗️ Build System

Sertifikita uses a two-step build process:

### 1. Build the macOS .app (PyInstaller)
This bundles the Python application into a standalone macOS `.app`.
```bash
bash scripts/build_py.sh
open dist-python/Sertifikita.app
```

### 2. Build the DMG (Electron Launcher)
We use a tiny Electron "silent launcher" to provide a familiar DMG installation experience and bypass certain Python path issues on macOS.
```bash
bash scripts/build_dmg.sh
open electron/dist/Sertifikita-*.dmg
```

## 🗂️ Project Structure

```
Sertifikita/
├─ app/
│  ├─ main.py               # UI (PySide6)
│  ├─ renderer.py           # Drawing logic (Pillow / ReportLab)
│  └─ resources/            # Assets (fonts, images, QSS)
├─ electron/
│  ├─ main.js               # Silent launcher (starts Python app)
│  └─ package.json          # electron-builder config (DMG)
├─ scripts/
│  ├─ build_py.sh           # PyInstaller build script
│  ├─ build_dmg.sh          # Electron DMG build script
├─ Sertifikita.spec         # PyInstaller configuration
└─ .github/workflows/       # CI/CD (GitHub Actions)
```

## 🧪 CI/CD
The project includes a GitHub Actions workflow (`.github/workflows/build-macos.yml`) that triggers on tags (e.g., `v1.0.0`) to build and attach the DMG to a GitHub Release.

To release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🛠️ Troubleshooting

- **macOS Gatekeeper**: If you get an "unidentified developer" error, right-click the app → **Open**. Or run:
  `xattr -dr com.apple.quarantine dist-python/Sertifikita.app`
- **Logs**:
  - Launcher: `~/Library/Logs/sertifikita-launch.log`
  - Python app: `~/Library/Logs/sertifikita-python.err.log`

## 🗣️ Contributing
Pull requests are welcome! Please ensure you test your changes by running the app locally before submitting.
