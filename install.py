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
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOME = Path.home()

# Where each harness looks for skills. Add a row to support a new harness.
TARGETS = {
    "claude": HOME / ".claude" / "skills",
    "cursor": HOME / ".cursor" / "skills",
    "codex": HOME / ".codex" / "skills",
    "vault": HOME / "Owen's Awesome Vault" / ".claude" / "skills",
}


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

    changes = 0

    # 1. Prune links into this repo that are no longer manifested.
    for harness, target in TARGETS.items():
        if not target.is_dir():
            continue
        for entry in sorted(target.iterdir()):
            if not entry.is_symlink():
                continue
            try:
                dest = Path(os.readlink(entry))
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
    for name, harness in sorted(wanted):
        target = TARGETS[harness]
        link, src = target / name, REPO / "skills" / name
        if link.is_symlink() and Path(os.readlink(link)) == src:
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
    print(f"{len(wanted)} link(s) manifested, {changes} {verb}.")


if __name__ == "__main__":
    main()
