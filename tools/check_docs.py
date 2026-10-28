"""Check Markdown paths, runnable Mozhi fences and generated documentation links."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mozhi.cli import parse


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def check():
    failures, snippets = [], 0
    sources = list((ROOT / "docs").rglob("*.md")) + list(ROOT.glob("*.md"))
    sources += list((ROOT / "packaging").rglob("*.md"))
    for file in sources:
        text = file.read_text(encoding="utf-8")
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text):
            failures.append(f"{file.relative_to(ROOT)}: unexpected control character")
        for target in re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            if not (file.parent / unquote(url.path)).exists():
                failures.append(f"{file.relative_to(ROOT)}: missing Markdown target {target}")
        for source in re.findall(r"^```mozhi[ \t]*\n(.*?)^```", text, re.M | re.S):
            try:
                parse(source)
                snippets += 1
            except (SyntaxError, ValueError) as error:
                failures.append(f"{file.relative_to(ROOT)}: invalid Mozhi snippet: {error}")

    site = ROOT / "site"
    if not (site / "learn/index.html").is_file():
        raise SystemExit("Build the combined site with tools/build_site.py first")
    cache = {}

    def document(path):
        if path not in cache:
            cache[path] = Links(path.read_text(encoding="utf-8"))
        return cache[path]

    links = 0
    for file in (site / "learn").rglob("*.html"):
        for target in document(file).links:
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if path.startswith("/mozhi/"):
                resolved = site / path[len("/mozhi/"):]
            elif path.startswith("/"):
                resolved = site / path.lstrip("/")
            else:
                resolved = (file.parent / path).resolve() if path else file
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.is_file():
                failures.append(f"{file.relative_to(site)}: missing rendered target {target}")
                continue
            links += 1
            if url.fragment and resolved.suffix == ".html" and unquote(url.fragment) not in document(resolved).ids:
                failures.append(f"{file.relative_to(site)}: missing fragment {target}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS {len(sources)} Markdown files, {snippets} runnable Mozhi snippets and {links} rendered links/assets")


if __name__ == "__main__":
    check()
