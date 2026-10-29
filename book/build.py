"""Assemble the interactive textbook into a static site.

    python book/build.py            # writes _site/
    python book/build.py --serve    # builds, then serves http://localhost:8000

The site is the book/ folder plus copies of finance101/, examples/ and tests/
so the browser can load and run every .py file. GitHub Actions runs this
script and publishes _site/ to GitHub Pages.
"""

import argparse
import functools
import http.server
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
PYTHON_FOLDERS = ("examples", "finance101", "tests")


def build(out: Path) -> dict:
    toc = json.loads((BOOK / "toc.json").read_text())
    missing = [
        ch["slug"]
        for course in toc["courses"]
        for ch in course["chapters"]
        if not (BOOK / "chapters" / f"{ch['slug']}.md").exists()
    ]
    if missing:
        raise SystemExit(f"toc.json lists chapters with no Markdown file: {missing}")

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(BOOK, out, ignore=shutil.ignore_patterns("*.py", "__pycache__"))
    files = {}
    for folder in PYTHON_FOLDERS:
        shutil.copytree(ROOT / folder, out / folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        files[folder] = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).glob("*.py"))
    manifest = {"files": files}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (out / ".nojekyll").touch()  # serve files exactly as they are
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=ROOT / "_site")
    parser.add_argument("--serve", action="store_true", help="serve the site after building")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    manifest = build(args.out)
    count = sum(len(v) for v in manifest["files"].values())
    print(f"Built {args.out} ({count} Python files available in the browser)")
    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.out))
        print(f"Serving on http://localhost:{args.port}  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
