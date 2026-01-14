# Sertifikita - Developer Documentation

This document contains technical information for developers who want to contribute to Sertifikita or build it from source.

## 🛠️ Development Setup

### Prerequisites
- Python 3.10 – 3.13
- Node.js & NPM (required only for building the DMG)

### Local Development Environment
```bash
# 1) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r app/requirements.txt

# 3) Launch the development UI
python app/main.py
```

## 🏗️ Build System

Sertifikita uses a two-step build process on macOS:

### 1. Build the macOS .app (PyInstaller)
This bundles the Python application into a standalone macOS `.app` bundle.
```bash
bash scripts/build_py.sh
open dist-python/Sertifikita.app
```

### 2. Build the DMG (Electron Launcher)
We use a lightweight Electron "silent launcher" to provide a standard macOS DMG installation experience and handle path resolution for the Python bundle.
```bash
bash scripts/build_dmg.sh
open electron/dist/Sertifikita-*.dmg
```

## 🗂️ Project Structure

```
Sertifikita/
├─ app/
│  ├─ main.py               # Core UI logic (PySide6)
│  ├─ renderer.py           # Rendering Engine (Pillow / ReportLab)
│  └─ resources/            # Assets (fonts, images, QSS themes)
├─ electron/
│  ├─ main.js               # Silent launcher (starts the bundled Python app)
│  └─ package.json          # electron-builder configuration for DMG
├─ scripts/
│  ├─ build_py.sh           # PyInstaller automation script
│  ├─ build_dmg.sh          # Electron DMG build automation script
├─ Sertifikita.spec         # PyInstaller specification file
└─ .github/workflows/       # CI/CD Workflows (GitHub Actions)
```

## 🧪 CI/CD
The project uses GitHub Actions (`.github/workflows/build-macos.yml`) to automatically build and attach the DMG to GitHub Releases whenever a new tag is pushed (e.g., `v1.0.0`).

To trigger a release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🛠️ Troubleshooting

- **macOS Gatekeeper**: If you encounter an "unidentified developer" warning, right-click the app → **Open**. Alternatively, you can clear the quarantine attribute:
  `xattr -dr com.apple.quarantine dist-python/Sertifikita.app`
- **Logs**:
  - Launcher logs: `~/Library/Logs/sertifikita-launch.log`
  - Python application logs: `~/Library/Logs/sertifikita-python.err.log`

## 🗣️ Contributing
Pull requests are highly encouraged! Please ensure you test your changes locally before submitting a PR.
