"""Contract tests for the portable skills catalog export."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / "scripts" / "export_catalog.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatalogContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.write_skill("zulu", "Full description. Use when the entire trigger matters.")
        self.write_skill("alpha", "Alpha | description.")
        self.write_manifest({
            "schema_version": 1,
            "skills": {
                "zulu": ["vault", "codex"],
                "alpha": ["cursor", "claude"],
            },
        })

    def write_skill(self, name, description):
        folder = self.repo / "skills" / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n# {name}\n",
            encoding="utf-8",
        )

    def write_manifest(self, manifest):
        (self.repo / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

    def write_quoted_description(self, name, description):
        source = self.repo / "skills" / name / "SKILL.md"
        source.write_text(
            f"---\nname: {name}\ndescription: {json.dumps(description)}\n---\n# {name}\n",
            encoding="utf-8",
        )

    def run_exporter(self, env=None):
        return subprocess.run(
            [sys.executable, str(EXPORTER), "--repo", str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def installer_result(self):
        installer = load("catalog_contract_installer", ROOT / "install.py")
        installer.REPO = self.repo
        with contextlib.redirect_stdout(io.StringIO()):
            return installer.main(["--check"])

    def test_export_is_deterministic_sorted_and_complete(self):
        first = self.run_exporter()
        second = self.run_exporter()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, "")

        catalog = json.loads(first.stdout)
        self.assertEqual(set(catalog), {"schema_version", "skills"})
        self.assertEqual(catalog["schema_version"], 1)
        self.assertEqual([skill["name"] for skill in catalog["skills"]], ["alpha", "zulu"])
        self.assertEqual(
            set(catalog["skills"][0]),
            {"name", "description", "source", "targets"},
        )
        self.assertEqual(catalog["skills"][0]["targets"], ["claude", "cursor"])
        self.assertEqual(catalog["skills"][1]["targets"], ["codex", "vault"])
        self.assertEqual(catalog["skills"][1]["description"],
                         "Full description. Use when the entire trigger matters.")
        self.assertEqual(catalog["skills"][1]["source"], "skills/zulu/SKILL.md")

    def test_current_catalog_is_unique_and_matches_manifest(self):
        result = subprocess.run(
            [sys.executable, str(EXPORTER), "--repo", str(ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog = json.loads(result.stdout)
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        names = [skill["name"] for skill in catalog["skills"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names, sorted(manifest["skills"]))
        for skill in catalog["skills"]:
            self.assertFalse(Path(skill["source"]).is_absolute())
            self.assertTrue((ROOT / skill["source"]).is_file())

    def test_legacy_manifest_is_schema_v1_for_installer_and_exporter(self):
        self.write_manifest({"skills": {"alpha": ["codex"]}})
        result = self.run_exporter()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["schema_version"], 1)
        self.assertEqual(self.installer_result(), 0)

    def test_unsupported_version_is_rejected_without_partial_json(self):
        self.write_manifest({"schema_version": 2, "skills": {"alpha": ["codex"]}})
        result = self.run_exporter()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("unsupported schema_version 2", result.stderr)
        self.assertEqual(self.installer_result(), 1)

    def test_malformed_version_is_rejected_without_partial_json(self):
        for version in ("1", 1.0, True, None):
            with self.subTest(version=version):
                self.write_manifest({
                    "schema_version": version,
                    "skills": {"alpha": ["codex"]},
                })
                result = self.run_exporter()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("schema_version must be an integer", result.stderr)
                self.assertEqual(self.installer_result(), 1)

    def test_manifest_schema_evolution_does_not_change_export_schema(self):
        scripts = str(ROOT / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
            self.addCleanup(sys.path.remove, scripts)
        contract = __import__("catalog_contract")
        exporter = load("catalog_schema_independence", EXPORTER)
        self.write_manifest({"schema_version": 2, "skills": {"alpha": ["codex"]}})
        with patch.object(contract, "MANIFEST_SCHEMA_VERSION", 2):
            catalog = exporter.export_catalog(self.repo)
        self.assertEqual(catalog["schema_version"], 1)

    def test_ascii_stdout_locale_exports_unicode_description(self):
        self.write_skill("alpha", "Café workflow.")
        env = dict(__import__("os").environ)
        env["PYTHONIOENCODING"] = "ascii"
        result = self.run_exporter(env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            json.loads(result.stdout)["skills"][0]["description"],
            "Café workflow.",
        )
        self.assertIn(r"Caf\u00e9 workflow.", result.stdout)

    def test_lone_surrogate_is_rejected_by_installer_and_exporter(self):
        source = self.repo / "skills" / "zulu" / "SKILL.md"
        source.write_text(
            '---\nname: zulu\ndescription: "\\ud800"\n---\n# zulu\n',
            encoding="utf-8",
        )
        result = self.run_exporter()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("lone Unicode surrogate", result.stderr)
        self.assertEqual(self.installer_result(), 1)

    def test_line_break_characters_never_emit_partial_json(self):
        for separator in ("\r", "\n", "\u2028", "\u2029"):
            with self.subTest(separator=repr(separator)):
                self.write_quoted_description("zulu", f"Before{separator}After")
                result = self.run_exporter()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("expected a nonempty one-line string", result.stderr)

    def test_renderer_rejects_line_separator_without_corrupting_table(self):
        vault = Path(self.tmp.name) / "line-separator-vault"
        moc = vault / "01-Maps" / "MOC - Agent Skills.md"
        moc.parent.mkdir(parents=True)
        moc.write_text("## Skills\nOld table\n## Claude Agents\nTail\n", encoding="utf-8")
        before = moc.read_bytes()
        self.write_quoted_description("zulu", "Before\u2028After")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "render_vault_inventory.py"),
             "--repo", str(self.repo), "--vault", str(vault)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("expected a nonempty one-line string", result.stderr)
        self.assertEqual(moc.read_bytes(), before)

    def test_exporter_rejects_internal_and_external_leaf_skill_symlinks(self):
        source = self.repo / "skills" / "zulu" / "SKILL.md"
        internal = self.repo / "internal-skill.md"
        external = Path(self.tmp.name) / "external-skill.md"
        content = "---\nname: zulu\ndescription: Linked.\n---\n# zulu\n"
        internal.write_text(content, encoding="utf-8")
        external.write_text(content, encoding="utf-8")
        for target in (internal, external):
            with self.subTest(target=target):
                source.unlink()
                source.symlink_to(target)
                result = self.run_exporter()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("expected a regular SKILL.md", result.stderr)

    def test_skills_ancestor_symlink_escape_is_rejected(self):
        escaped_repo = Path(self.tmp.name) / "escaped-repo"
        escaped_repo.mkdir()
        external = Path(self.tmp.name) / "external-skills"
        skill = external / "demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: demo\ndescription: Escaped.\n---\n# demo\n",
            encoding="utf-8",
        )
        (escaped_repo / "skills").symlink_to(external, target_is_directory=True)
        (escaped_repo / "manifest.json").write_text(
            json.dumps({"schema_version": 1, "skills": {"demo": ["codex"]}}),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(EXPORTER), "--repo", str(escaped_repo)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("expected a local regular directory", result.stderr)

    def test_inventory_check_invalid_input_does_not_create_lock(self):
        vault = Path(self.tmp.name) / "vault"
        (vault / "01-Maps").mkdir(parents=True)
        (vault / "01-Maps" / "MOC - Agent Skills.md").write_text(
            "## Skills\nOld\n## Claude Agents\nTail\n", encoding="utf-8"
        )
        self.write_manifest({"schema_version": 2, "skills": {"alpha": ["vault"]}})
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "render_vault_inventory.py"),
             "--repo", str(self.repo), "--vault", str(vault), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / ".install.lock").exists())

    def test_second_validation_failure_preserves_links_and_inventory(self):
        vault = Path(self.tmp.name) / "vault"
        moc = vault / "01-Maps" / "MOC - Agent Skills.md"
        moc.parent.mkdir(parents=True)
        moc.write_text("## Skills\nOld\n## Claude Agents\nTail\n", encoding="utf-8")
        target = vault / ".claude" / "skills"
        target.mkdir(parents=True)
        link = target / "alpha"
        link.symlink_to(self.repo / "skills" / "alpha", target_is_directory=True)
        before_inventory = moc.read_bytes()

        installer = load("catalog_second_validation_installer", ROOT / "install.py")
        installer.REPO = self.repo
        installer.TARGETS = {"vault": (vault, ".claude/skills")}
        with patch.object(
            installer,
            "load_manifest",
            side_effect=[
                ({("alpha", "vault")}, []),
                (set(), ["manifest.json: unsupported schema_version 2"]),
            ],
        ), contextlib.redirect_stdout(io.StringIO()):
            result = installer.main(["--target", "vault"])
        self.assertEqual(result, 1)
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), (self.repo / "skills" / "alpha").resolve())
        self.assertEqual(moc.read_bytes(), before_inventory)

    def test_invalid_schema_apply_preserves_owned_link_and_inventory(self):
        vault = Path(self.tmp.name) / "invalid-schema-vault"
        moc = vault / "01-Maps" / "MOC - Agent Skills.md"
        moc.parent.mkdir(parents=True)
        moc.write_text("## Skills\nOld\n## Claude Agents\nTail\n", encoding="utf-8")
        target = vault / ".claude" / "skills"
        target.mkdir(parents=True)
        link = target / "alpha"
        link.symlink_to(self.repo / "skills" / "alpha", target_is_directory=True)
        before_inventory = moc.read_bytes()
        self.write_manifest({"schema_version": 2, "skills": {"alpha": ["vault"]}})

        installer = load("catalog_invalid_apply_installer", ROOT / "install.py")
        installer.REPO = self.repo
        installer.TARGETS = {"vault": (vault, ".claude/skills")}
        with contextlib.redirect_stdout(io.StringIO()):
            result = installer.main(["--target", "vault"])
        self.assertEqual(result, 1)
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), (self.repo / "skills" / "alpha").resolve())
        self.assertEqual(moc.read_bytes(), before_inventory)

    def test_late_skill_errors_never_emit_partial_json(self):
        source = self.repo / "skills" / "zulu" / "SKILL.md"
        invalid_sources = (
            b"---\nname: zulu\n---\n# zulu\n",
            b"---\nname: zulu\ndescription: \xff\n---\n# zulu\n",
        )
        for content in invalid_sources:
            with self.subTest(content=content):
                source.write_bytes(content)
                result = self.run_exporter()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_shared_target_registry_matches_installer(self):
        contract = load("catalog_target_registry", ROOT / "scripts" / "catalog_contract.py")
        installer = load("catalog_target_installer", ROOT / "install.py")
        self.assertEqual(set(installer.TARGETS), set(contract.TARGET_NAMES))


if __name__ == "__main__":
    unittest.main()
