#!/usr/bin/env python3
"""Validate and link this repository's skills. Stdlib only; no changes on errors.

--check validates the catalog; --dry-run also previews installation.
Only symlinks into this checkout's skills directory are managed. Install from
the permanent checkout after integrating changes, never a temporary worktree.
Applying installs use a local lock, stage the vault inventory, and roll back
ordinary filesystem failures where possible.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent
HOME = Path.home()
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from catalog_contract import TARGET_LAYOUTS, install_lock, load_catalog  # noqa: E402

TARGETS = {
    name: (HOME / root, subpath)
    for name, (root, subpath) in TARGET_LAYOUTS.items()
}


def readlink(path):
    """Normalize absolute and relative links, including Windows prefixes."""
    dest = os.readlink(path)
    if dest.startswith("\\\\?\\"):
        dest = dest[4:]
        if dest.startswith("UNC\\"):
            dest = "\\\\" + dest[4:]
    dest = Path(dest)
    return Path(os.path.abspath(dest if dest.is_absolute() else path.parent / dest))


def load_manifest():
    try:
        rows = load_catalog(REPO)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        return set(), [str(exc)]
    wanted = {(name, harness) for name, _, harnesses in rows for harness in harnesses}
    return wanted, []


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


def inventory_module():
    """Load the optional vault inventory renderer from this checkout."""
    path = REPO / "scripts" / "render_vault_inventory.py"
    spec = importlib.util.spec_from_file_location("skills_inventory", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load inventory renderer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _path_state(path):
    if path.is_symlink():
        return ("symlink", os.readlink(path))
    if path.exists():
        return ("other", None)
    return ("absent", None)


def _source_ready(src):
    return (src.is_dir() and not src.is_symlink() and
            (src / "SKILL.md").is_file() and not (src / "SKILL.md").is_symlink())


class ApplyFailure(RuntimeError):
    def __init__(self, operation, rollback_errors=()):
        self.operation = operation
        self.rollback_errors = tuple(rollback_errors)
        detail = f"{operation}; links were rolled back"
        if self.rollback_errors:
            detail += "; rollback incomplete: " + "; ".join(self.rollback_errors)
        super().__init__(detail)


class LinkTransaction:
    def __init__(self, before, desired, intermediate, touched, changed, created_dirs):
        self.before = before
        self.desired = desired
        self.intermediate = intermediate
        self.touched = touched
        self.changed = changed
        self.created_dirs = created_dirs


def _restore_state(path, before, desired, intermediate, changed):
    current = _path_state(path)
    if current == before:
        return
    if path not in changed:
        raise RuntimeError(f"target changed unexpectedly during rollback: {path}")
    if current != desired and current != intermediate:
        raise RuntimeError(f"refusing to remove unmanaged path during rollback: {path}")
    if current[0] == "symlink":
        path.unlink()
    if before[0] == "symlink":
        path.symlink_to(before[1], target_is_directory=True)
    elif before[0] != "absent":
        raise RuntimeError(f"unsupported rollback state for {path}: {before[0]}")


def rollback_links(transaction):
    errors = []
    seen = set()
    for path in reversed(transaction.touched):
        if path in seen:
            continue
        seen.add(path)
        try:
            _restore_state(
                path,
                transaction.before[path],
                transaction.desired[path],
                transaction.intermediate[path],
                transaction.changed,
            )
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    for directory in reversed(transaction.created_dirs):
        try:
            if directory.is_dir() and not directory.is_symlink():
                directory.rmdir()
        except OSError as exc:
            errors.append(f"{directory}: {exc}")
    return errors


def _prepare_parents(actions):
    created = []
    try:
        for _, link, _ in actions:
            if link.parent.exists():
                continue
            missing, current = [], link.parent
            while not current.exists() and current != current.parent:
                missing.append(current)
                current = current.parent
            link.parent.mkdir(parents=True, exist_ok=True)
            # ``missing`` is leaf-to-ancestor; keep created dirs
            # ancestor-to-leaf so rollback can remove deepest first.
            created.extend(path for path in reversed(missing) if path.is_dir() and not path.is_symlink())
    except Exception:
        for directory in reversed(created):
            try:
                if directory.is_dir() and not directory.is_symlink():
                    directory.rmdir()
            except OSError:
                pass
        raise
    return created


def apply_links(actions):
    before = {}
    desired = {}
    intermediate = {}
    for action, link, src in actions:
        state = _path_state(link)
        if action == "unlink" and state[0] != "symlink":
            raise ApplyFailure(f"target changed before unlink: {link}")
        if state[0] == "symlink" and not owned(link):
            raise ApplyFailure(f"foreign symlink appeared before apply: {link}")
        if action == "link" and state[0] == "other":
            raise ApplyFailure(f"unmanaged path appeared before link: {link}")
        if action == "link" and not _source_ready(src):
            raise ApplyFailure(f"skill source changed before link: {src}")
        before[link] = state
        desired[link] = ("absent", None) if action == "unlink" else ("symlink", str(src))
        # A replacement deliberately passes through an absent path after the
        # old owned link is removed and before the new link is created.
        intermediate[link] = ("absent", None)
    created_dirs = _prepare_parents(actions)
    touched = []
    changed = set()
    transaction = LinkTransaction(
        before, desired, intermediate, touched, changed, created_dirs
    )
    try:
        for action, link, src in actions:
            if _path_state(link) != before[link]:
                raise RuntimeError(f"target changed during install: {link}")
            touched.append(link)
            try:
                if action == "unlink":
                    link.unlink()
                    changed.add(link)
                else:
                    if link.is_symlink():
                        link.unlink()
                        changed.add(link)
                    link.symlink_to(src, target_is_directory=True)
                    changed.add(link)
            except Exception:
                if _path_state(link) != before[link]:
                    changed.add(link)
                raise
    except Exception as exc:
        rollback_errors = rollback_links(transaction)
        raise ApplyFailure(str(exc), rollback_errors) from exc
    return transaction


def _selected_plan(wanted, selected):
    all_targets, all_absent = live_targets()
    targets = {harness: target for harness, target in all_targets.items() if harness in selected}
    absent = [(harness, root) for harness, root in all_absent if harness in selected]
    filtered = {(name, harness) for name, harness in wanted if harness in selected}
    actions, problems = installation_plan(filtered, targets)
    return targets, absent, actions, problems


def _print_manifest_error(problems):
    for problem in problems:
        print(f"ERROR {problem}")
    print("No links changed.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--target",
        action="append",
        choices=sorted(TARGETS),
        help="limit installation to this harness (repeat for several harnesses)",
    )
    args = parser.parse_args(argv)
    wanted, problems = load_manifest()
    if problems:
        _print_manifest_error(problems)
        return 1
    print(f"Validated {len({n for n, _ in wanted})} skills, {len(wanted)} target mappings.")
    if args.check:
        return 0
    if (REPO / ".git").is_file() and not args.dry_run:
        print("ERROR apply from the permanent checkout after integrating this worktree; use --dry-run here.")
        return 1
    selected = set(args.target or TARGETS)

    def show_plan(absent, actions, plan_problems, dry=False):
        for harness, root in absent:
            print(f"SKIP {harness}: {root} is absent")
        if plan_problems:
            for problem in plan_problems:
                print(f"ERROR {problem}")
            print("No links changed.")
            return False
        for action, link, _ in actions:
            print(f"{'WOULD ' if dry else ''}{action.upper()} {link}")
        return True

    if args.dry_run:
        targets, absent, actions, plan_problems = _selected_plan(wanted, selected)
        if not show_plan(absent, actions, plan_problems, dry=True):
            return 1
        if "vault" in targets:
            try:
                inventory = inventory_module()
                inventory_plan = inventory.plan_update(REPO, TARGETS["vault"][0])
            except (OSError, ValueError, KeyError, RuntimeError) as exc:
                print(f"ERROR vault skills inventory: {exc}")
                print("No links changed.")
                return 1
            if inventory_plan.changed:
                print("WOULD UPDATE vault skills inventory")
        print(f"{len(actions)} link changes planned.")
        return 0

    try:
        with install_lock(REPO):
            # Re-read the catalog and targets after taking the lock. Another
            # cooperating installer may have changed either while we waited.
            wanted, problems = load_manifest()
            if problems:
                _print_manifest_error(problems)
                return 1
            targets, absent, actions, plan_problems = _selected_plan(wanted, selected)
            if not show_plan(absent, actions, plan_problems):
                return 1

            inventory = None
            inventory_plan = None
            if "vault" in targets:
                inventory = inventory_module()
                inventory_plan = inventory.plan_update(REPO, TARGETS["vault"][0])
                inventory.stage_update(inventory_plan)

            transaction = None
            try:
                transaction = apply_links(actions)
                if inventory is not None:
                    inventory.commit_update(inventory_plan)
            except Exception as exc:
                rollback_errors = []
                if transaction is not None:
                    rollback_errors = rollback_links(transaction)
                if inventory_plan is not None:
                    try:
                        inventory.discard_update(inventory_plan)
                    except Exception as discard_exc:
                        rollback_errors.append(f"inventory staging cleanup: {discard_exc}")
                if isinstance(exc, ApplyFailure):
                    rollback_errors = list(exc.rollback_errors) + rollback_errors
                    print(f"ERROR {ApplyFailure(exc.operation, rollback_errors)}")
                else:
                    message = f"{exc}; links were rolled back"
                    if rollback_errors:
                        message += "; rollback incomplete: " + "; ".join(rollback_errors)
                    print(f"ERROR {message}")
                return 1
            finally:
                if inventory_plan is not None:
                    inventory.discard_update(inventory_plan)
            if inventory_plan is not None and inventory_plan.changed:
                print("UPDATED vault skills inventory")
            print(f"{len(actions)} link changes applied.")
            return 0
    except OSError as exc:
        print(f"ERROR cannot acquire installer lock or access the checkout: {exc}")
        print("No links changed.")
        return 1
    except (ValueError, KeyError, RuntimeError) as exc:
        print(f"ERROR {exc}")
        print("No links changed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
