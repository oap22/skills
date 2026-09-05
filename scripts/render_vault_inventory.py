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
import json
import os
from pathlib import Path
import re
import stat
import tempfile

START = "<!-- skills-inventory:start -->"
END = "<!-- skills-inventory:end -->"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HARNESSES = {"claude", "cursor", "codex", "vault"}
_START_LINE = re.compile(r"^[ \t]*" + re.escape(START) + r"[ \t]*(?:\n|$)", re.M)
_END_LINE = re.compile(r"^[ \t]*" + re.escape(END) + r"[ \t]*(?:\n|$)", re.M)
_SKILLS_HEADING = re.compile(r"^[ \t]{0,3}##[ \t]+Skills[ \t]*$", re.M)
_AGENTS_HEADING = re.compile(r"^[ \t]{0,3}##[ \t]+Claude Agents[ \t]*$", re.M)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _scalar(value):
    """Parse the same deliberately small string subset as install.py."""
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


def _frontmatter(name, source):
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"{name}: cannot read SKILL.md: {exc}") from exc
    block = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not block:
        raise ValueError(f"{name}: missing frontmatter delimiters")
    fields = {}
    for line in block[1].splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep or key not in {"name", "description"}:
            raise ValueError(f"{name}: unsupported frontmatter field/structure: {key!r}")
        if key in fields:
            raise ValueError(f"{name}: duplicate {key}")
        try:
            fields[key] = _scalar(value.strip())
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{name}: invalid {key}: {exc}") from exc
    if fields.get("name") != name:
        raise ValueError(f"{name}: frontmatter name must match directory")
    description = fields.get("description")
    if not description:
        raise ValueError(f"{name}: missing valid description")
    if len(description) > 1024:
        raise ValueError(f"{name}: description exceeds 1024 characters")
    if not text[block.end():].strip():
        raise ValueError(f"{name}: empty skill body")
    return description


def _catalog(repo):
    try:
        manifest = json.loads(
            (repo / "manifest.json").read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest.json: {exc}") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("skills"), dict):
        raise ValueError("manifest.json: manifest must contain a skills object")

    rows = []
    for name, targets in sorted(manifest["skills"].items()):
        if not isinstance(name, str) or len(name) > 64 or not NAME.fullmatch(name):
            raise ValueError(f"invalid skill name: {name!r}")
        if not isinstance(targets, list) or not targets:
            raise ValueError(f"{name}: targets must be a nonempty list")
        seen = set()
        for target in targets:
            if not isinstance(target, str) or target not in HARNESSES:
                raise ValueError(f"{name}: unknown harness {target!r}")
            if target in seen:
                raise ValueError(f"{name}: duplicate harness {target}")
            seen.add(target)
        folder = repo / "skills" / name
        source = folder / "SKILL.md"
        if folder.is_symlink() or not folder.is_dir() or source.is_symlink() or not source.is_file():
            raise ValueError(f"{name}: expected a local skill directory with a regular SKILL.md")
        description = _frontmatter(name, source)
        rows.append((name, description, targets))
    return rows


def render(repo):
    rows = []
    for name, description, targets in _catalog(repo):
        # This is display text, never a link target or executable instruction.
        description = description.split(" Use when", 1)[0]
        if len(description) > 190:
            description = description[:187].rsplit(" ", 1)[0] + "…"
        description = description.replace("|", "\\|").replace("\n", " ")
        rows.append(f"| `{name}` | {description} | {', '.join(targets)} |")
    return "\n".join([
        START,
        "Generated from `~/Developer/active/skills/manifest.json` and each skill's description. The installer refreshes this block; edit the source skill rather than this table.",
        "",
        "| Skill | Purpose | Harnesses |",
        "|---|---|---|",
        *rows,
        END,
    ])


def _fenced_and_headings(text):
    """Return genuine heading spans, excluding fenced code blocks."""
    in_fence = None
    skills, agents = [], []
    offset = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        fence = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", body)
        if fence:
            marker = fence.group(1)
            if in_fence is None:
                in_fence = (marker[0], len(marker))
            elif marker[0] == in_fence[0] and len(marker) >= in_fence[1]:
                in_fence = None
            offset += len(line)
            continue
        if in_fence is None:
            if _SKILLS_HEADING.fullmatch(body):
                skills.append((offset, offset + len(line)))
            if _AGENTS_HEADING.fullmatch(body):
                agents.append((offset, offset + len(line)))
        offset += len(line)
    return skills, agents


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
    skills, agents = _fenced_and_headings(text)
    start = starts[0]
    end = ends[0]
    # Marker lines inside fences are never a managed region.
    fenced_lines = []
    in_fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        fence = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", body)
        if fence:
            marker = fence.group(1)
            if in_fence is None:
                in_fence = (marker[0], len(marker))
            elif marker[0] == in_fence[0] and len(marker) >= in_fence[1]:
                in_fence = None
        elif in_fence is not None:
            fenced_lines.append((offset, offset + len(line)))
        offset += len(line)
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

    skills, agents = _fenced_and_headings(text)
    if len(skills) != 1 or len(agents) != 1 or skills[0][0] >= agents[0][0]:
        raise ValueError("legacy inventory requires one unique unfenced Skills heading before Claude Agents")
    # Preserve the old section verbatim after the managed block. This makes the
    # first migration safe even when the legacy list contains user-authored text.
    insert_at = skills[0][1]
    intro = "\nSource of truth: `~/Developer/active/skills`. Edit there and run `./install.py`; do not hand-place managed skills. See [[.system/skills-portability]].\n\n"
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
    with _local_lock(repo):
        plan = plan_update(repo, vault)
        if check:
            return not plan.changed
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
