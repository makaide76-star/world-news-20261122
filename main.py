#!/usr/bin/env python3
"""Write the 22 November 2026 entry image to the output directory.

Stdlib only, no network, fully deterministic. The finished front page is
checked into the repo at assets/entry.png (drawn by tools/make_image.py
from the verified wire headlines of Sunday 22 November 2026) and this
script copies it byte for byte, so every run produces identical output.

Output location: $ENTRY_OUTPUT_DIR/entry.png, defaulting to /output/entry.png.
"""
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUNDLED = ROOT / "assets" / "entry.png"


def destination() -> Path:
    out_dir = Path(os.environ.get("ENTRY_OUTPUT_DIR", "/output"))
    return out_dir / "entry.png"


def run() -> Path:
    target = destination()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(BUNDLED, target)
    return target


if __name__ == "__main__":
    written = run()
    print(f"wrote {written} ({written.stat().st_size} bytes)")
