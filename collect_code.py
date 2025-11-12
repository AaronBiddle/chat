# !/usr/bin/env python3
"""Collect .py (or other) files from the project into a single text file.

Place this file in your project root and run it. By default it:
- searches from the current directory
- collects files with extension .py
- excludes common folders (.venv, venv, env, .git, __pycache__, node_modules, build, dist, .mypy_cache)
- excludes the output file itself to avoid recursion

Usage:
  python collect_code.py [--root PATH] [--output code.txt] [--exclude NAME ...] [--ext .py .pyi]

The output will contain simple separators with the relative path for each file.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable, List, Set


DEFAULT_EXCLUDES: Set[str] = {
    ".venv",
    "venv",
    "env",
    ".git",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    ".mypy_cache",
}


def find_files(root: Path, extensions: Iterable[str], excludes: Set[str], output_path: Path) -> List[Path]:
    """Walk root and return a list of file Paths matching extensions while skipping excluded dirs.

    - root: path to start from
    - extensions: iterable of lowercase extensions, e.g. {'.py'}
    - excludes: set of directory basenames to skip
    - output_path: path to output file (to exclude it)
    """
    matches: List[Path] = []
    root = root.resolve()
    out_name = output_path.resolve()

    script_path = Path(__file__).resolve()

    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        # filter out excluded directories so os.walk won't descend into them
        dirnames[:] = [d for d in dirnames if d not in excludes]

        # avoid descending into symlinked directories
        dirnames[:] = [d for d in dirnames if not (Path(dirpath) / d).is_symlink()]

        for fn in filenames:
            p = Path(dirpath) / fn
            # Skip the output file itself and this script file
            try:
                resolved = p.resolve()
                if resolved == out_name or resolved == script_path:
                    continue
            except Exception:
                # resolution problems -> skip the comparison
                pass

            if p.suffix.lower() in extensions:
                matches.append(p)

    matches.sort()
    return matches


def write_aggregated(files: List[Path], root: Path, out: Path) -> None:
    """Write all files to out, with simple headers separating them."""
    root = root.resolve()
    with out.open("w", encoding="utf-8", errors="replace") as fh:
        for p in files:
            try:
                rel = p.resolve().relative_to(root)
            except Exception:
                rel = p.resolve()

            fh.write(f"### FILE: {rel}\n")
            fh.write("### " + "-" * 70 + "\n")
            try:
                with p.open("r", encoding="utf-8", errors="replace") as src:
                    fh.write(src.read())
            except OSError as e:
                fh.write(f"# FAILED TO READ: {e}\n")
            fh.write("\n\n")


def main() -> int:
    """Run the collector with zero args:

    - root: current working directory
    - output: code.txt in cwd (overwritten)
    - extensions: .py only
    - excludes: DEFAULT_EXCLUDES plus output filename
    """
    root = Path(os.getcwd())
    out = Path("code.txt")

    excludes = set(DEFAULT_EXCLUDES)
    excludes.add(out.name)

    exts = {".py"}

    files = find_files(root, exts, excludes, out)
    write_aggregated(files, root, out)

    print(f"Wrote {len(files)} files to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
