#!/usr/bin/env python3
"""Entrypoint for the 22 November 2026 front-page image.

Builds the page through tools/make_image.py, then checks the result
before handing it over: the file must start with the PNG magic bytes,
measure exactly 1024x1024, and stay under the 1 MiB entry cap.
The finished file lands in ENTRY_OUTPUT_DIR when that variable is
set, otherwise in the repo's own assets/ folder.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tools"))

import make_image  # noqa: E402

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SIZE_LIMIT = 1_048_576
EXPECTED_SIDE = 1024


def _png_dimensions(blob):
    """Read width/height out of the IHDR chunk of a PNG byte string."""
    if blob[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file: bad magic bytes")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def _fingerprint(path):
    """Return (sha256 hex, byte count) for the file at `path`."""
    digest = hashlib.sha256()
    total = 0
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
            total += len(chunk)
    return digest.hexdigest(), total


def _destination():
    """Pick the output folder: env override wins, assets/ is the default."""
    override = os.environ.get("ENTRY_OUTPUT_DIR")
    if override:
        return Path(override).expanduser()
    return HERE / "assets"


def main():
    out_dir = _destination()
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"

    make_image.render(target)

    blob = target.read_bytes()
    width, height = _png_dimensions(blob)
    if (width, height) != (EXPECTED_SIDE, EXPECTED_SIDE):
        raise SystemExit(
            f"bad dimensions: {width}x{height}, expected "
            f"{EXPECTED_SIDE}x{EXPECTED_SIDE}"
        )
    if len(blob) > SIZE_LIMIT:
        raise SystemExit(
            f"file too large: {len(blob)} bytes exceeds {SIZE_LIMIT}"
        )

    checksum, nbytes = _fingerprint(target)
    print(f"output: {target}")
    print(f"size: {nbytes} bytes")
    print(f"sha256: {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
