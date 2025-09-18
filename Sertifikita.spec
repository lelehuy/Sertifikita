# Sertifikita.spec — FIX: sertakan PYZ ke EXE, lalu COLLECT → BUNDLE
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

ROOT_DIR = Path.cwd()          # build_py.sh memastikan CWD = root proyek
APP_DIR  = ROOT_DIR / "app"
MAIN_PY  = APP_DIR / "main.py"

datas = [
    (str(APP_DIR / "resources" / "templates"), "resources/templates"),
    (str(APP_DIR / "resources" / "fonts"),     "resources/fonts"),
    (str(APP_DIR / "resources" / "images"),    "resources/images"),
    (str(APP_DIR / "resources" / "qss"),       "resources/qss"),
]

a = Analysis(
    [str(MAIN_PY)],
    pathex=[str(APP_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=collect_submodules("PIL"),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

# arsip bytecode Python
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# executable: PASTIKAN pyz jadi argumen pertama
exe = EXE(
    pyz,                      # <<-- ini kunci
    a.scripts,
    [],
    exclude_binaries=True,    # biner & data dipindah ke COLLECT
    name="Sertifikita",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(APP_DIR / "resources" / "images" / "icon.icns"),
)

# kumpulkan semua file pendukung
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="Sertifikita"
)

# bungkus jadi macOS .app bundle
app = BUNDLE(
    coll,
    name="Sertifikita.app",
    icon=str(APP_DIR / "resources" / "images" / "icon.icns"),
    bundle_identifier="com.sertifikita.app",
    info_plist={
        "CFBundleName": "Sertifikita",
        "CFBundleDisplayName": "Sertifikita",
        "CFBundleIdentifier": "com.sertifikita.app",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "CFBundleIconFile": "icon.icns",
        "LSMinimumSystemVersion": "10.13"
    }
)
