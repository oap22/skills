#!/usr/bin/env python3
"""Symlink skills from this repo into each agent harness, per manifest.json.

Idempotent. Also prunes stale links that point into this repo but are no
longer listed in the manifest, so removing a skill from the manifest and
re-running is enough to deactivate it everywhere.

    ./install.py            apply
    ./install.py --dry-run  show what would change
"""

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOME = Path.home()

# Where each harness looks for skills, as (root, subpath). The root is the
# directory that must already exist for the harness to count as installed on
# this machine; a harness whose root is absent is skipped rather than
# conjured into being. Add a row to support a new harness.
TARGETS = {
    "claude": (HOME / ".claude", "skills"),
    "cursor": (HOME / ".cursor", "skills"),
    "codex": (HOME / ".codex", "skills"),
    "vault": (HOME / "Owen's Awesome Vault", ".claude/skills"),
}


def readlink(path):
    r"""The symlink's stored destination, normalized across platforms.

    Windows os.readlink() returns the extended-length form (\\?\C:\...),
    which never compares equal to a plain Path — left unstripped, every link
    looks wrong (so it is needlessly recreated every run) and no link looks
    like it points into this repo (so stale links are never pruned). On
    POSIX the prefix never appears and this is a passthrough.
    """
    dest = os.readlink(path)
    if dest.startswith("\\\\?\\"):
        dest = dest[4:]
        if dest.startswith("UNC\\"):
            dest = "\\\\" + dest[4:]
    return Path(dest)


def live_targets():
    """Skills dir per harness, omitting harnesses not installed here."""
    dirs, absent = {}, []
    for harness, (root, sub) in TARGETS.items():
        if root.is_dir():
            dirs[harness] = root / sub
        else:
            absent.append((harness, root))
    return dirs, absent


def frontmatter_problems(name):
    """Flag frontmatter that parses badly and silently unroutes a skill.

    Every harness routes on the description string, so a description that
    fails to parse is a skill that never fires — with no error anywhere.
    """
    text = (REPO / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    block = re.match(r"---\n(.*?)\n---", text, re.S)
    if not block:
        return [f"{name}: SKILL.md has no frontmatter block"]

    fields = {}
    for line in block.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not key.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()

    problems = []
    if fields.get("name") != name:
        problems.append(f"{name}: frontmatter name is {fields.get('name')!r}")

    description = fields.get("description", "")
    if not description:
        problems.append(f"{name}: frontmatter has no description")
    elif description[0] not in "\"'" and ": " in description:
        problems.append(
            f"{name}: description is an unquoted YAML scalar containing ': ' — "
            "it will not parse, and the skill will never route"
        )
    return problems


def load_manifest():
    path = REPO / "manifest.json"
    try:
        skills = json.loads(path.read_text()).get("skills", {})
    except FileNotFoundError:
        sys.exit(f"no manifest at {path}")
    except json.JSONDecodeError as e:
        sys.exit(f"manifest.json is not valid JSON: {e}")

    wanted, problems = set(), []
    for name, harnesses in skills.items():
        if not (REPO / "skills" / name / "SKILL.md").exists():
            problems.append(f"skills/{name}/SKILL.md missing")
            continue
        problems.extend(frontmatter_problems(name))
        for h in harnesses:
            if h not in TARGETS:
                problems.append(f"{name}: unknown harness {h!r}")
            else:
                wanted.add((name, h))
    return wanted, problems


def main():
    dry = "--dry-run" in sys.argv
    wanted, problems = load_manifest()
    for p in problems:
        print(f"  ! {p}")

    targets, absent = live_targets()
    for harness, root in absent:
        print(f"  - skipped {harness}: {root} is not on this machine")

    changes = 0

    # 1. Prune links into this repo that are no longer manifested.
    for harness, target in targets.items():
        if not target.is_dir():
            continue
        for entry in sorted(target.iterdir()):
            if not entry.is_symlink():
                continue
            try:
                dest = readlink(entry)
            except OSError:
                continue
            if REPO not in dest.parents:
                continue  # not ours; leave it alone
            if (entry.name, harness) not in wanted:
                print(f"  {'would unlink' if dry else 'unlinked'}    {entry}")
                if not dry:
                    entry.unlink()
                changes += 1

    # 2. Create or refresh the manifested links.
    linkable = sorted((n, h) for n, h in wanted if h in targets)
    for name, harness in linkable:
        target = targets[harness]
        link, src = target / name, REPO / "skills" / name
        if link.is_symlink() and readlink(link) == src:
            continue  # already correct
        if link.exists() and not link.is_symlink():
            print(f"  ! {link} is a real directory — not overwriting")
            continue
        print(f"  {'would link' if dry else 'linked'}      {link}")
        if not dry:
            target.mkdir(parents=True, exist_ok=True)
            if link.is_symlink():
                link.unlink()
            link.symlink_to(src)
        changes += 1

    verb = "would change" if dry else "changed"
    skipped = len(wanted) - len(linkable)
    tail = f" ({skipped} awaiting an absent harness)" if skipped else ""
    print(f"{len(linkable)} link(s) manifested here{tail}, {changes} {verb}.")


if __name__ == "__main__":
    main()
