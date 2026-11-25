#!/usr/bin/env python3
"""Place the finished front page where the grader expects it.

render.py draws the picture and saves it next to this file as entry.png.
This runner only copies those exact bytes into the output directory, so
every grading run writes identical bytes. No clock, no network, no
randomness, nothing read from outside the repository.
"""

import os
import shutil
import sys
from pathlib import Path

OUTPUT_ENV = "MAKEFUN_OUTPUT_DIR"
SOURCE_NAME = "entry.png"


def picture_path() -> Path:
    return Path(__file__).resolve().parent / SOURCE_NAME


def destination_dir() -> Path:
    return Path(os.environ.get(OUTPUT_ENV, "out"))


def place() -> int:
    src = picture_path()
    if not src.is_file():
        print(f"missing picture: {src}", file=sys.stderr)
        return 1
    out = destination_dir()
    out.mkdir(parents=True, exist_ok=True)
    target = out / SOURCE_NAME
    shutil.copyfile(src, target)
    print(f"placed {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(place())
