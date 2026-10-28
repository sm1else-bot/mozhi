"""Build the studio and documentation as one relocatable static website."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def main():
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(SITE / "learn")],
        cwd=ROOT, check=True,
    )
    for folder in ("playground", "examples"):
        shutil.copytree(ROOT / folder, SITE / folder, dirs_exist_ok=True)
    shutil.copyfile(ROOT / "docs/assets/favicon.svg", SITE / "favicon.svg")
    (SITE / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta http-equiv="refresh" content="0;url=playground/">'
        '<link rel="icon" type="image/svg+xml" href="favicon.svg">'
        '<title>Mozhi</title></head><body><a href="playground/">Open Mozhi Studio</a></body></html>\n',
        encoding="utf-8",
    )
    print(f"Website built in {SITE}. Preview: python -m http.server 8000 --directory site")


if __name__ == "__main__":
    main()
