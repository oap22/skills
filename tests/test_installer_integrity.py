"""Failure-path tests for installer and vault inventory integrity."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.skill = self.repo / "skills" / "demo"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(
            "---\nname: demo\ndescription: Example skill.\n---\n# Demo\n"
        )
        self.manifest = self.repo / "manifest.json"
        self.manifest.write_text(json.dumps({"skills": {"demo": ["codex"]}}))
        self.home = self.root / "harness"
        self.home.mkdir()
        self.target = self.home / "skills"
        self.target.mkdir()
        self.installer = load("installer_integrity", ROOT / "install.py")
        self.installer.REPO = self.repo
        self.installer.TARGETS = {"codex": (self.home, "skills")}
        self.inventory = load("inventory_integrity", ROOT / "scripts/render_vault_inventory.py")

    def run_installer(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.installer.main(list(args))

    def use_vault(self, content=None):
        vault = self.root / "vault"
        (vault / "01-Maps").mkdir(parents=True)
        moc = vault / "01-Maps" / "MOC - Agent Skills.md"
        moc.write_text(content or "## Skills\nOld list\n## Claude Agents\nTail\n")
        self.manifest.write_text(json.dumps({"skills": {"demo": ["vault"]}}))
        self.installer.TARGETS = {"vault": (vault, ".claude/skills")}
        return vault, moc


class InventoryIntegrityTests(Fixture):
    def test_legacy_migration_ignores_fenced_headings_and_preserves_text(self):
        vault, moc = self.use_vault(
            "Intro\n```md\n## Skills\nexample\n## Claude Agents\nexample tail\n```\n"
            "## Skills\nLegacy list\n## Claude Agents\nReal tail\n"
        )
        self.inventory.update_inventory(self.repo, vault)
        text = moc.read_text()
        self.assertIn("example tail", text)
        self.assertIn("Legacy list", text)
        self.assertEqual(text.count(self.inventory.START), 1)
        self.assertLess(text.index("Legacy list"), text.index("## Claude Agents\nReal tail"))

    def test_ambiguous_legacy_headings_fail_without_writing(self):
        vault, moc = self.use_vault("## Skills\nOne\n## Skills\nTwo\n## Claude Agents\nTail\n")
        before = moc.read_bytes()
        with self.assertRaises(ValueError):
            self.inventory.update_inventory(self.repo, vault)
        self.assertEqual(moc.read_bytes(), before)

    def test_standalone_renderer_rejects_malformed_targets(self):
        vault, moc = self.use_vault()
        self.manifest.write_text('{"skills":{"demo":"codex"}}')
        before = moc.read_bytes()
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/render_vault_inventory.py"),
             "--repo", str(self.repo), "--vault", str(vault)],
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(moc.read_bytes(), before)

    def test_atomic_replace_failure_preserves_moc(self):
        vault, moc = self.use_vault()
        before = moc.read_bytes()
        with patch.object(self.inventory.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                self.inventory.update_inventory(self.repo, vault)
        self.assertEqual(moc.read_bytes(), before)
        self.assertEqual(list(moc.parent.glob(f".{moc.name}.*.tmp")), [])

    def test_invalid_closing_fence_keeps_example_markers_fenced(self):
        vault, moc = self.use_vault(
            "```md\n"
            "```not-a-close\n"
            "<!-- skills-inventory:start -->\n"
            "example\n"
            "<!-- skills-inventory:end -->\n"
            "## Skills\nLegacy\n## Claude Agents\nTail\n"
        )
        before = moc.read_bytes()
        with self.assertRaises(ValueError):
            self.inventory.update_inventory(self.repo, vault)
        self.assertEqual(moc.read_bytes(), before)


class InstallerIntegrityTests(Fixture):
    def test_read_only_inventory_is_rejected_before_link_changes(self):
        vault, moc = self.use_vault()
        moc.chmod(0o444)
        self.assertEqual(self.run_installer("--target", "vault"), 1)
        self.assertFalse((vault / ".claude/skills/demo").exists())

    def test_late_inventory_failure_rolls_back_links(self):
        vault, moc = self.use_vault()
        inventory = self.inventory
        before = moc.read_bytes()
        with patch.object(self.installer, "inventory_module", return_value=inventory), \
                patch.object(inventory, "commit_update", side_effect=OSError("commit failed")):
            self.assertEqual(self.run_installer("--target", "vault"), 1)
        self.assertFalse((vault / ".claude/skills/demo").exists())
        self.assertFalse((vault / ".claude").exists())
        self.assertEqual(moc.read_bytes(), before)

    def test_link_failure_restores_owned_prune(self):
        old_source = self.repo / "skills" / "old"
        old_source.mkdir()
        (self.target / "old").symlink_to(old_source)
        original = Path.symlink_to
        failed = False

        def fail_new(path, target, target_is_directory=False):
            nonlocal failed
            if path.name == "demo" and not failed:
                failed = True
                raise OSError("simulated link failure")
            return original(path, target, target_is_directory=target_is_directory)

        with patch.object(Path, "symlink_to", fail_new):
            self.assertEqual(self.run_installer(), 1)
        self.assertTrue((self.target / "old").is_symlink())
        self.assertFalse((self.target / "demo").exists())

    def test_replacement_failure_restores_exact_owned_target(self):
        old_source = self.repo / "skills" / "old"
        old_source.mkdir()
        old_target = os.path.relpath(old_source, self.target)
        link = self.target / "demo"
        link.symlink_to(old_target)
        original = Path.symlink_to
        failed = False

        def fail_new(path, target, target_is_directory=False):
            nonlocal failed
            if path == link and not failed:
                failed = True
                raise OSError("simulated replacement failure")
            return original(path, target, target_is_directory=target_is_directory)

        with patch.object(Path, "symlink_to", fail_new):
            self.assertEqual(self.run_installer(), 1)
        self.assertTrue(failed)
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), old_target)
        self.assertEqual(os.path.realpath(link), os.path.realpath(old_source))

    def test_foreign_symlink_appearing_after_plan_is_preserved(self):
        original_plan = self.installer.installation_plan
        foreign = self.root / "foreign"

        def race_plan(wanted, targets):
            actions, problems = original_plan(wanted, targets)
            if actions:
                (self.target / "demo").symlink_to(foreign)
            return actions, problems

        with patch.object(self.installer, "installation_plan", race_plan):
            self.assertEqual(self.run_installer(), 1)
        self.assertEqual(os.readlink(self.target / "demo"), str(foreign))

    def test_cooperating_installs_serialize_and_replan(self):
        original = Path.symlink_to
        entered = threading.Event()
        release = threading.Event()
        first = True

        def slow_first(path, target, target_is_directory=False):
            nonlocal first
            if path.name == "demo" and first:
                first = False
                entered.set()
                self.assertTrue(release.wait(5))
            return original(path, target, target_is_directory=target_is_directory)

        results = []

        def run():
            results.append(self.run_installer())

        with patch.object(Path, "symlink_to", slow_first):
            first_thread = threading.Thread(target=run)
            first_thread.start()
            self.assertTrue(entered.wait(5))
            second_thread = threading.Thread(target=run)
            second_thread.start()
            time.sleep(0.1)
            self.assertTrue(second_thread.is_alive())
            release.set()
            first_thread.join(5)
            second_thread.join(5)
        self.assertEqual(sorted(results), [0, 0])
        self.assertTrue((self.target / "demo").is_symlink())


if __name__ == "__main__":
    unittest.main()
