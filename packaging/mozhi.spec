from pathlib import Path
import os
import sys

root = Path(SPECPATH).parent
analysis = Analysis(
    [str(root / "packaging" / "entrypoint.py")],
    pathex=[str(root / "src")], binaries=[], datas=[],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False,
)
archive = PYZ(analysis.pure)
exe = EXE(
    archive, analysis.scripts, analysis.binaries, analysis.datas, [],
    name="mozhi", debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=True,
    version=str(root / "build" / "windows-version.txt") if sys.platform == "win32" else None,
    codesign_identity=os.environ.get("MOZHI_CODESIGN_IDENTITY"),
)
