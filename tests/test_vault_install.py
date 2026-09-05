import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / "skills/demo").mkdir(parents=True)
        (self.repo / "skills/demo/SKILL.md").write_text("---\nname: demo\ndescription: Example.\n---\n\n# Demo\n")
        self.manifest = self.repo / "manifest.json"
        self.manifest.write_text(json.dumps({"skills": {"demo": ["codex"]}}))
        self.installer = load("installer", REPO / "install.py")
        self.installer.REPO = self.repo
        for target in ["codex", "cursor"]:
            (self.root / target).mkdir()
        self.installer.TARGETS = {target: (self.root / target, "skills") for target in ["codex", "cursor"]}

    def run_installer(self, *args):
        return self.installer.main(list(args))

    def test_targeted_install_and_idempotence(self):
        self.assertEqual(0, self.run_installer("--target", "codex"))
        link = self.root / "codex/skills/demo"
        self.assertTrue(link.is_symlink())
        stamp = link.lstat().st_mtime_ns
        self.assertEqual(0, self.run_installer("--target", "codex"))
        self.assertEqual(stamp, link.lstat().st_mtime_ns)
        self.assertFalse((self.root / "cursor/skills").exists())

    def test_invalid_manifest_does_not_prune_existing_link(self):
        self.run_installer("--target", "codex")
        self.manifest.write_text(json.dumps({"skills": {"missing": ["codex"]}}))
        self.assertEqual(1, self.run_installer("--target", "codex"))
        self.assertTrue((self.root / "codex/skills/demo").is_symlink())

    def test_real_directory_conflict_is_preserved_and_fails(self):
        (self.root / "codex/skills/demo").mkdir(parents=True)
        self.assertEqual(1, self.run_installer("--target", "codex"))
        self.assertFalse((self.root / "codex/skills/demo").is_symlink())

    def test_dry_run_writes_nothing(self):
        self.assertEqual(0, self.run_installer("--target", "codex", "--dry-run"))
        self.assertFalse((self.root / "codex/skills").exists())

    def test_vault_target_refreshes_inventory(self):
        inventory = load("inventory_for_installer", REPO / "scripts/render_vault_inventory.py")
        vault = self.root / "vault"
        (vault / "01-Maps").mkdir(parents=True)
        moc = vault / "01-Maps/MOC - Agent Skills.md"
        moc.write_text("## Skills\nOld list\n## Claude Agents\nTail\n")
        self.manifest.write_text(json.dumps({"skills": {"demo": ["vault"]}}))
        self.installer.TARGETS = {"vault": (vault, ".claude/skills")}
        with patch.object(self.installer, "inventory_module", return_value=inventory):
            self.assertEqual(0, self.run_installer("--target", "vault"))
        self.assertTrue((vault / ".claude/skills/demo").is_symlink())
        self.assertIn(inventory.START, moc.read_text())
        self.assertTrue(moc.read_text().endswith("## Claude Agents\nTail\n"))


class InventoryTests(unittest.TestCase):
    def test_regeneration_preserves_surrounding_content(self):
        module = load("inventory", REPO / "scripts/render_vault_inventory.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            skill = repo / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Example.\n---\n# Demo\n"
            )
            (repo / "manifest.json").write_text(json.dumps({"skills": {"demo": ["vault"]}}))
            vault = root / "vault"
            (vault / "01-Maps").mkdir(parents=True)
            path = vault / "01-Maps/MOC - Agent Skills.md"
            path.write_text("User intro\n## Skills\nOld list\n## Claude Agents\nUser tail\n")
            module.update_inventory(repo, vault)
            first = path.read_text()
            self.assertTrue(first.startswith("User intro\n"))
            self.assertTrue(first.endswith("## Claude Agents\nUser tail\n"))
            self.assertTrue(module.update_inventory(repo, vault, check=True))
            module.update_inventory(repo, vault)
            self.assertEqual(path.read_text(), first)
            self.assertEqual(first.count(module.START), 1)


if __name__ == "__main__":
    unittest.main()
