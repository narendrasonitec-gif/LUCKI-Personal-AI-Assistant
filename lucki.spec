# PyInstaller onedir build. The custom Lucki icon is applied to the EXE.
from pathlib import Path

root = Path(SPECPATH)
assets = root / "assets"
generated = root / "generated"

datas = []
if assets.exists():
    datas.append((str(assets), "assets"))
if generated.exists():
    datas.append((str(generated), "generated"))

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "edge_tts",
        "pygame",
        "google.genai",
        "speech_recognition",
        "pyautogui",
        "pyperclip",
        "pypdf",
        "PIL",
        "reportlab",
        "pptx",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
icon_path = assets / "lucki_icon.ico"
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Lucki",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Lucki",
)
