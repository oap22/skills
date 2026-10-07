#!/usr/bin/env python3
"""Print folder names that appear in more than one place in the home layout.

Checks the project-level folders only (not the files inside a project), with a
case-insensitive compare because macOS file names are case-insensitive. Also
prints folders nested inside a parent of the same name. Prints nothing and
exits 0 when the layout is clean; exits 1 when it finds a problem.

Usage: find_dupes.py [--home DIR]
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

# (relative root, max depth). A folder with .git is a project: the scan
# records it and does not look inside it. A folder without .git is recorded,
# and the scan goes one level deeper until max depth.
ROOTS = [
    ("code", 3),       # code/<ctx>/<repo>, code/sch/<course>/<repo>
    ("life", 1),
    ("ref", 1),
    ("arc", 1),
    ("Developer", 5),  # old layout, until it is gone
    ("Areas", 1),
    ("Resources", 1),
    ("Archives", 1),
]
# Top-level folders that the OS or apps own
SKIP_TOP = {"Library", "Applications", "Movies", "Music", "Pictures", "Public",
            "Documents", "Desktop", "Downloads", "Dropbox"}


def is_dir(p: Path) -> bool:
    try:
        return p.is_dir()
    except OSError:  # app-owned or protected folder
        return False


def children(p: Path) -> list[Path]:
    try:
        return [c for c in sorted(p.iterdir())
                if not c.name.startswith(".") and is_dir(c)]
    except OSError:
        return []


def walk(root: Path, depth: int, out: list[Path]) -> None:
    for c in children(root):
        out.append(c)
        if depth > 1 and not (c / ".git").exists():
            walk(c, depth - 1, out)


def scan(home: Path) -> list[str]:
    seen: dict[str, list[Path]] = defaultdict(list)
    for name, depth in ROOTS:
        root = home / name
        if is_dir(root) and not root.is_symlink():
            found: list[Path] = []
            walk(root, depth, found)
            for p in found:
                seen[p.name.lower()].append(p)
    root_names = {r.lower() for r, _ in ROOTS}
    for p in children(home):
        if p.name not in SKIP_TOP and p.name.lower() not in root_names:
            seen[p.name.lower()].append(p)
    problems = []
    for key, paths in sorted(seen.items()):
        if len(paths) > 1:
            listed = ", ".join(str(x.relative_to(home)) for x in paths)
            problems.append(f"duplicate '{key}': {listed}")
        for p in paths:
            # A repo's own layout (skills/skills) is not checked.
            if not (p / ".git").exists() and any(
                    c.name.lower() == key for c in children(p)):
                problems.append(f"nested same name: {p.relative_to(home)}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--home", type=Path, default=Path.home())
    args = ap.parse_args()
    problems = scan(args.home.expanduser())
    for line in problems:
        print(line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
