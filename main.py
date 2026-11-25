#!/usr/bin/env python3
"""Run the news-image-20261125 entry: hand the finished picture to the grader.

render.py paints the front page and stores it as entry.png beside this file.
All this program does is move that exact file into the directory the grader
names through MAKEFUN_OUTPUT_DIR (or ./out when the variable is absent).
Moving bytes cannot change them, so each run writes the same picture.
"""

import pathlib
import sys
from os import environ
from shutil import copyfile

PICTURE = "entry.png"


def _picture_file():
    return pathlib.Path(__file__).resolve().parent / PICTURE


def _target_dir():
    return pathlib.Path(environ.get("MAKEFUN_OUTPUT_DIR", "out"))


def run():
    picture = _picture_file()
    if not picture.exists():
        print("no picture to place:", picture, file=sys.stderr)
        return 1
    folder = _target_dir()
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / PICTURE
    copyfile(picture, target)
    print("wrote", target, target.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
