#!/usr/bin/env python3
"""Generate the managed Skills inventory in the vault MOC.

The inventory is deliberately a small, validated projection of ``manifest.json``.
Only the marked block is replaced once it exists. A first run may migrate a
legacy MOC when it contains one unique, unfenced ``## Skills`` heading followed
by one unique, unfenced ``## Claude Agents`` heading; the old section content is
kept after the new managed block.
"""
import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from catalog_contract import load_catalog  # noqa: E402

START = "<!-- skills-inventory:start -->"
END = "<!-- skills-inventory:end -->"
_START_LINE = re.compile(r"^[ \t]*" + re.escape(START) + r"[ \t]*(?:\n|$)", re.M)
_END_LINE = re.compile(r"^[ \t]*" + re.escape(END) + r"[ \t]*(?:\n|$)", re.M)
_SKILLS_HEADING = re.compile(r"^[ \t]{0,3}##[ \t]+Skills[ \t]*$", re.M)
_AGENTS_HEADING = re.compile(r"^[ \t]{0,3}##[ \t]+Claude Agents[ \t]*$", re.M)


# Compatibility for callers that used the former private helper. New code
# should use load_catalog().
_catalog = load_catalog


def render(repo):
    rows = []
    for name, description, targets in load_catalog(repo):
        # This is display text, never a link target or executable instruction.
        description = description.split(" Use when", 1)[0]
        if len(description) > 190:
            description = description[:187].rsplit(" ", 1)[0] + "…"
        description = description.replace("|", "\\|").replace("\n", " ")
        rows.append(f"| `{name}` | {description} | {', '.join(targets)} |")
    return "\n".join([
        START,
        "Generated from `~/Developer/active/personal/skills/manifest.json` and each skill's description. The installer refreshes this block; edit the source skill rather than this table.",
        "",
        "| Skill | Purpose | Harnesses |",
        "|---|---|---|",
        *rows,
        END,
    ])


def _fenced_and_headings(text):
    """Return genuine headings and lines inside fenced code blocks.

    A closing fence must use the opening fence character, be at least as
    long, and have only whitespace after it. This matches Markdown fence
    rules closely enough for migration safety: a fence followed by text such
    as ``not-a-close`` remains fenced content rather than silently exposing
    example headings or markers.
    """
    in_fence = None
    skills, agents, fenced_lines = [], [], []
    offset = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        fence = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$", body)
        if fence:
            marker = fence.group(1)
            if in_fence is None:
                in_fence = (marker[0], len(marker))
            elif (marker[0] == in_fence[0] and len(marker) >= in_fence[1]
                  and not fence.group(2).strip()):
                in_fence = None
            elif in_fence is not None:
                fenced_lines.append((offset, offset + len(line)))
            offset += len(line)
            continue
        if in_fence is None:
            if _SKILLS_HEADING.fullmatch(body):
                skills.append((offset, offset + len(line)))
            if _AGENTS_HEADING.fullmatch(body):
                agents.append((offset, offset + len(line)))
        else:
            fenced_lines.append((offset, offset + len(line)))
        offset += len(line)
    return skills, agents, fenced_lines


def _marker_region(text):
    start_occurrences = list(re.finditer(re.escape(START), text))
    end_occurrences = list(re.finditer(re.escape(END), text))
    starts = list(_START_LINE.finditer(text))
    ends = list(_END_LINE.finditer(text))
    if len(start_occurrences) != len(starts) or len(end_occurrences) != len(ends):
        raise ValueError("inventory markers must occupy complete, unambiguous lines")
    if not start_occurrences and not end_occurrences:
        return None
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError("inventory markers missing or duplicated")
    _, _, fenced_lines = _fenced_and_headings(text)
    start = starts[0]
    end = ends[0]
    # Marker lines inside fences are never a managed region.
    if any(a <= start.start() < b or a <= end.start() < b for a, b in fenced_lines):
        raise ValueError("inventory marker is inside a fenced block")
    if start.start() > end.start():
        raise ValueError("inventory markers reversed")
    return start.start(), end.end()


def _replace_block(text, block):
    region = _marker_region(text)
    if region is not None:
        start, end = region
        before, after = text[:start], text[end:]
        if after and not block.endswith("\n"):
            block += "\n"
        return before + block + after

    skills, agents, _ = _fenced_and_headings(text)
    if len(skills) != 1 or len(agents) != 1 or skills[0][0] >= agents[0][0]:
        raise ValueError("legacy inventory requires one unique unfenced Skills heading before Claude Agents")
    # Preserve the old section verbatim after the managed block. This makes the
    # first migration safe even when the legacy list contains user-authored text.
    insert_at = skills[0][1]
    intro = "\nSource of truth: `~/Developer/active/personal/skills`. Edit there and run `./install.py`; do not hand-place managed skills. See [[.system/skills-portability]].\n\n"
    return text[:insert_at] + intro + block + "\n" + text[insert_at:]


class InventoryPlan:
    def __init__(self, path, before, after):
        self.path = path
        self.before = before
        self.after = after
        self.temp = None

    @property
    def changed(self):
        return self.before != self.after


def plan_update(repo, vault):
    path = vault / "01-Maps" / "MOC - Agent Skills.md"
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"inventory path must be a regular file: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read inventory: {exc}") from exc
    return InventoryPlan(path, text, _replace_block(text, render(repo)))


def stage_update(plan):
    if not plan.changed:
        return
    path = plan.path
    if path.is_symlink() or not path.is_file():
        raise OSError(f"inventory path changed or is not a regular file: {path}")
    mode = stat.S_IMODE(path.stat().st_mode)
    if not mode & 0o222:
        raise PermissionError(f"inventory file is read-only: {path}")
    try:
        current = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise OSError(f"cannot revalidate inventory: {exc}") from exc
    if current != plan.before:
        raise RuntimeError("inventory changed while preparing installation; retry")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    plan.temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(plan.after)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(plan.temp, mode)
    except BaseException:
        try:
            plan.temp.unlink(missing_ok=True)
        finally:
            plan.temp = None
        raise


def commit_update(plan):
    if not plan.changed:
        return
    if plan.temp is None:
        raise RuntimeError("inventory update was not staged")
    if plan.path.is_symlink() or not plan.path.is_file():
        raise OSError(f"inventory path changed before commit: {plan.path}")
    if plan.path.read_text(encoding="utf-8") != plan.before:
        raise RuntimeError("inventory changed before commit; retry")
    os.replace(plan.temp, plan.path)
    plan.temp = None


def discard_update(plan):
    if plan.temp is not None:
        plan.temp.unlink(missing_ok=True)
        plan.temp = None


@contextmanager
def _local_lock(repo):
    """Serialize direct inventory writers using the install lock."""
    lock_path = repo / ".install.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as handle:
        try:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            unlock = lambda: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except ImportError:  # pragma: no cover - exercised on Windows only.
            import msvcrt
            handle.seek(0)
            handle.write("0")
            handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            unlock = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        try:
            yield
        finally:
            unlock()


def update_inventory(repo, vault, check=False):
    # Validate and render before creating the lock. Read-only checks should not
    # leave filesystem state behind, and invalid input must fail before any
    # mutation. Applying recomputes under the lock to close the validation race.
    initial_plan = plan_update(repo, vault)
    if check:
        return not initial_plan.changed
    with _local_lock(repo):
        plan = plan_update(repo, vault)
        try:
            stage_update(plan)
            commit_update(plan)
        finally:
            discard_update(plan)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--vault", type=Path, default=Path.home() / "Owen's Awesome Vault")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        ok = update_inventory(args.repo, args.vault, args.check)
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        parser.exit(2, f"Inventory error: {exc}\n")
    if not ok:
        parser.exit(1, "Skills inventory differs from manifest; rerun without --check.\n")
    print("Skills inventory matches manifest." if args.check else "Skills inventory generated.")


if __name__ == "__main__":
    main()
