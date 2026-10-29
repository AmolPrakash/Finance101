"""Run every ```python run cell in every chapter, in order, the way a reader would.

    python book/check_chapters.py                 # all chapters
    python book/check_chapters.py 02 10           # chapters whose slug starts with 02 or 10
    python book/check_chapters.py -v 02           # also print each cell's output

Cells in one chapter share a namespace (like the browser does). The script
exits non-zero if any cell raises, so CI catches broken examples. A cell
tagged ```python run error is a deliberate mistake and must raise.
"""

import contextlib
import io
import json
import os
import re
import sys
import time
import traceback
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
CELL = re.compile(r"^```python run([^\n]*)\n(.*?)^```[ \t]*$", re.S | re.M)


def chapter_slugs():
    toc = json.loads((BOOK / "toc.json").read_text())
    return [ch["slug"] for course in toc["courses"] for ch in course["chapters"]] + ["resources"]


def run_chapter(slug: str, verbose: bool = False) -> int:
    source = (BOOK / "chapters" / f"{slug}.md").read_text()
    cells = CELL.findall(source)
    namespace = {"__name__": "__main__"}
    failures = 0
    start = time.perf_counter()
    for i, (flags, code) in enumerate(cells, start=1):
        expect_error = "error" in flags.split()
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                exec(compile(code, f"<{slug} cell {i}>", "exec"), namespace)
            if verbose:
                print(f"--- {slug} cell {i}\n{buffer.getvalue()}")
            if expect_error:
                failures += 1
                print(f"FAIL {slug} cell {i}: tagged 'error' but ran cleanly:\n{code}")
        except Exception:
            if not expect_error:
                failures += 1
                print(f"FAIL {slug} cell {i}:\n{code}\n{traceback.format_exc()}")
        finally:
            plt = sys.modules.get("matplotlib.pyplot")
            if plt is not None:
                plt.close("all")
    status = "ok" if not failures else f"{failures} failed"
    print(f"{slug:<40} {len(cells):>3} cells  {time.perf_counter() - start:5.1f}s  {status}")
    return failures


def main() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    warnings.filterwarnings("ignore", message=".*non-interactive.*")
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    verbose = "-v" in sys.argv
    prefixes = [arg for arg in sys.argv[1:] if arg != "-v"]
    slugs = [s for s in chapter_slugs() if not prefixes or s.startswith(tuple(prefixes))]
    failures = sum(run_chapter(slug, verbose) for slug in slugs)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
