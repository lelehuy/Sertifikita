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
