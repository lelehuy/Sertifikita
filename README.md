# Sertifikita

A lightweight desktop app to **design and batch-generate certificates**.  
Built with **PySide6 (Qt)** + **Pillow/ReportLab** for rendering, and packaged to a macOS **DMG** via a tiny **Electron launcher**.

> 🚀 Download: see the **Releases** tab for the latest `.dmg`.

---

## ✨ Features

- 🖼️ **Template-based**: use any PNG/JPG as your certificate background
- 🔤 **Dynamic text fields**: drag, resize, align (left/center/right), color, system fonts
- 🧭 **Live canvas**: resize text box directly on canvas, snap (5px), zoom slider
- 🗂️ **Manage Data**: inline table, CSV import/export, auto columns per field
- 🧩 **Filename pattern**: mix free text + `{row}` + `{FieldName}` tokens  
  _Example_: `"{row}-{Name}-{Course}"`
- 👀 **Preview**: quick render without saving
- 🖨️ **Generate**: batch export **PNG** or **PDF**
- 💾 **Save/Load fields JSON** (layout + field metadata)

---

## 🖥️ Install (end users)

1. Download the latest **`Sertifikita-<version>-arm64.dmg`** from **Releases**.
2. Open the DMG and **drag _Sertifikita_ into _Applications_**.
3. On macOS first run, right-click the app → **Open** (bypass Gatekeeper).

---

## 🧑‍💻 Run locally (development)

```bash
# 1) create venv
python3 -m venv .venv
source .venv/bin/activate

# 2) install deps
pip install -r app/requirements.txt

# 3) launch dev UI
python app/main.py
```

> Python 3.10–3.13 are supported. Uses **PySide6 ≥ 6.8**.

---

## 🏗️ Build

### Build the macOS .app (PyInstaller)

```bash
bash scripts/build_py.sh
open dist-python/Sertifikita.app
```

### Build the DMG (Electron + electron-builder)

```bash
bash scripts/build_dmg.sh
open electron/dist/Sertifikita-*.dmg
```

> The Electron app is only a **silent launcher** that starts the PyInstaller bundle and exits—no extra window.

---

## 🧩 Filename pattern tokens

Customize output filenames in **Data Export**:

- `{row}` – 1-based sequence number
- `{FieldName}` – any dynamic field key (e.g., `{Name}`, `{Course}`)

Examples:

- `"{row}-{Name}.png"` → `1-Agus.png`
- `"Cert-{Course}-{Name}"` → `Cert-UIUX-Agus.pdf`

---

## 📄 CSV format

- **Import**: first row is column headers; each column must match a field key (e.g., `Name,Course,...`).
- **Export**: current table as CSV with the same headers.

---

## 🖼️ Canvas tips

- **Resize text box**: drag the **blue handles** on the overlay
- **Align L/C/R**: visible on canvas and final render
- **Snap**: 5px grid (toggle in the right panel)
- **Zoom**: slider at the bottom

---

## 🗂️ Project structure

```
Sertifikita/
├─ app/
│  ├─ main.py               # UI (PySide6)
│  ├─ renderer.py           # drawing (Pillow / ReportLab)
│  └─ resources/
│     ├─ templates/         # sample templates (optional)
│     ├─ fonts/             # custom fonts (optional; uses system fonts too)
│     ├─ images/            # icon.icns, screenshots
│     └─ qss/               # stylesheets
├─ electron/
│  ├─ main.js               # silent launcher
│  ├─ package.json          # electron-builder config (DMG)
│  └─ build/
│     └─ icon.icns          # app icon (macOS)
├─ scripts/
│  ├─ build_py.sh           # build PyInstaller .app
│  ├─ build_dmg.sh          # build Electron DMG
│  └─ clean.sh              # remove build artifacts
├─ Sertifikita.spec         # PyInstaller spec (robust paths)
└─ .github/workflows/
   └─ build-macos.yml       # optional CI to build DMG on tag
```

---

## 🧪 CI (optional)

This repo includes a **GitHub Actions** workflow (`.github/workflows/build-macos.yml`) to build the DMG on macOS runners:

- Triggers on `workflow_dispatch` or `push` tags like `v1.0.0`.
- Uploads the DMG as an artifact and attaches it to the Release.

Create a tag to release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 🛠️ Troubleshooting

**macOS Gatekeeper / cannot open app**  
Right-click `Sertifikita.app` → **Open**. You can also clear quarantine:
```bash
xattr -dr com.apple.quarantine dist-python/Sertifikita.app
```

**Nothing happens after launch**  
Open logs:
- Launcher: `~/Library/Logs/sertifikita-launch.log`
- Python app: `~/Library/Logs/sertifikita-python.err.log`

**Qt platform plugin errors**  
Ensure you run the **.app bundle**:
```bash
open dist-python/Sertifikita.app
# or
dist-python/Sertifikita.app/Contents/MacOS/Sertifikita
```

---

## 🗣️ Contributing

PRs and issues are welcome!  
For bugs, please include steps to reproduce, expected vs actual behavior, and a sample template if possible.
