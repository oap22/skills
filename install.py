#!/usr/bin/env python3
"""Validate and link this repository's skills. Stdlib only; no changes on errors.

--check validates the catalog; --dry-run also previews installation.
Only symlinks into this checkout's skills directory are managed. Install from
the permanent checkout after integrating changes, never a temporary worktree.
"""
import argparse
import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOME = Path.home()
TARGETS = {
    "claude": (HOME / ".claude", "skills"),
    "cursor": (HOME / ".cursor", "skills"),
    "codex": (HOME / ".codex", "skills"),
    "vault": (HOME / "Owen's Awesome Vault", ".claude/skills"),
}
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def readlink(path):
    """Normalize absolute and relative links, including Windows prefixes."""
    dest = os.readlink(path)
    if dest.startswith("\\\\?\\"):
        dest = dest[4:]
        if dest.startswith("UNC\\"):
            dest = "\\\\" + dest[4:]
    dest = Path(dest)
    return Path(os.path.abspath(dest if dest.is_absolute() else path.parent / dest))


def scalar(value):
    """Accept this repo's deliberately small YAML string subset, fail closed.

    Plain one-line strings, JSON double-quoted strings, YAML single-quoted
    strings. This is not a general YAML parser; nested metadata/block scalars
    must be supported deliberately before using them in this catalog.
    """
    if value.startswith('"'):
        result = json.loads(value)
    elif value.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", value):
            raise ValueError("invalid single-quoted string")
        result = value[1:-1].replace("''", "'")
    else:
        if (not value or value[0] in "[]{}&*!|>@`%#,-?:" or
                ": " in value or " #" in value or
                value.lower() in {"true", "false", "null", "~", "yes", "no", "on", "off"} or
                re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value)):
            raise ValueError("quote this scalar with JSON double quotes")
        result = value
    if not isinstance(result, str) or not result.strip() or "\n" in result:
        raise ValueError("expected a nonempty one-line string")
    return result


def frontmatter_problems(name):
    try:
        text = (REPO / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"{name}: cannot read SKILL.md: {exc}"]
    block = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not block:
        return [f"{name}: missing frontmatter delimiters"]
    fields, problems = {}, []
    for line in block[1].splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep or key not in {"name", "description"}:
            problems.append(f"{name}: unsupported frontmatter field/structure: {key!r}")
            continue
        if key in fields:
            problems.append(f"{name}: duplicate {key}")
        try:
            fields[key] = scalar(value.strip())
        except (ValueError, TypeError) as exc:
            problems.append(f"{name}: invalid {key}: {exc}")
    if fields.get("name") != name:
        problems.append(f"{name}: frontmatter name must match directory")
    if not fields.get("description"):
        problems.append(f"{name}: missing valid description")
    if len(fields.get("description", "")) > 1024:
        problems.append(f"{name}: description exceeds 1024 characters")
    if not text[block.end():].strip():
        problems.append(f"{name}: empty skill body")
    return problems


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_manifest():
    try:
        data = json.loads((REPO / "manifest.json").read_text(), object_pairs_hook=unique_object)
        if not isinstance(data, dict) or not isinstance(data.get("skills"), dict):
            raise ValueError("manifest must contain a skills object")
    except (OSError, UnicodeError, ValueError) as exc:
        return set(), [f"manifest.json: {exc}"]
    wanted, problems = set(), []
    skills = data["skills"]
    for name, harnesses in skills.items():
        if len(name) > 64 or not NAME.fullmatch(name):
            problems.append(f"invalid skill name: {name!r}")
            continue
        folder = REPO / "skills" / name
        if folder.is_symlink() or not (folder / "SKILL.md").is_file() or (folder / "SKILL.md").is_symlink():
            problems.append(f"{name}: expected a local skill directory with a regular SKILL.md")
            continue
        problems.extend(frontmatter_problems(name))
        if not isinstance(harnesses, list) or not harnesses:
            problems.append(f"{name}: targets must be a nonempty list")
            continue
        seen = set()
        for harness in harnesses:
            if not isinstance(harness, str) or harness not in TARGETS:
                problems.append(f"{name}: unknown harness {harness!r}")
            elif harness in seen:
                problems.append(f"{name}: duplicate harness {harness}")
            else:
                wanted.add((name, harness))
                seen.add(harness)
    return wanted, problems


def live_targets():
    dirs, absent = {}, []
    for harness, (root, sub) in TARGETS.items():
        if root.is_dir():
            dirs[harness] = root / sub
        else:
            absent.append((harness, root))
    return dirs, absent


def owned(path):
    # Check direct stored destination, not resolve(): a foreign redirect is not ours.
    return path.is_symlink() and (REPO / "skills") in readlink(path).parents


def installation_plan(wanted, targets):
    actions, problems = [], []
    for harness, target in sorted(targets.items()):
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            problems.append(f"{target}: installation target is a symlink or non-directory")
            continue
        if target.is_dir():
            for entry in sorted(target.iterdir()):
                if owned(entry) and (entry.name, harness) not in wanted:
                    actions.append(("unlink", entry, None))
        for name, h in sorted(wanted):
            if h != harness:
                continue
            link, src = target / name, REPO / "skills" / name
            if link.is_symlink() and readlink(link) == src:
                continue
            if link.is_symlink() and not owned(link):
                problems.append(f"{link}: foreign symlink preserved; resolve the collision explicitly")
            elif link.exists() and not link.is_symlink():
                problems.append(f"{link}: unmanaged file/directory preserved")
            else:
                actions.append(("link", link, src))
    return actions, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    wanted, problems = load_manifest()
    if problems:
        for problem in problems:
            print(f"ERROR {problem}")
        print("No links changed.")
        return 1
    print(f"Validated {len({n for n, _ in wanted})} skills, {len(wanted)} target mappings.")
    if args.check:
        return 0
    # A temporary worktree must never become the destination of live links.
    if (REPO / ".git").is_file() and not args.dry_run:
        print("ERROR apply from the permanent checkout after integrating this worktree; use --dry-run here.")
        return 1
    targets, absent = live_targets()
    actions, problems = installation_plan(wanted, targets)
    for harness, root in absent:
        print(f"SKIP {harness}: {root} is absent")
    if problems:
        for problem in problems:
            print(f"ERROR {problem}")
        print("No links changed.")
        return 1
    for action, link, src in actions:
        print(f"{'WOULD ' if args.dry_run else ''}{action.upper()} {link}")
        if not args.dry_run:
            link.parent.mkdir(parents=True, exist_ok=True)
            if action == "unlink" or link.is_symlink():
                link.unlink()
            if action == "link":
                link.symlink_to(src, target_is_directory=True)
    print(f"{len(actions)} link changes{' planned' if args.dry_run else ' applied'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
