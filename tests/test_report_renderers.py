"""CLI behavior of the HTML report renderers bundled with adversarial-review and plan-then-ship."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "skills/adversarial-review/render_review.py"
PLAN = ROOT / "skills/plan-then-ship/render_plan.py"


class RendererTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, script, record):
        src = self.root / "record.json"
        src.write_text(json.dumps(record), encoding="utf-8")
        out = self.root / "nested" / "report.html"
        proc = subprocess.run([sys.executable, str(script), str(src), "--out", str(out)],
                              capture_output=True, text=True, timeout=10)
        return proc, out


class ReviewRendererTests(RendererTestCase):
    def test_findings_sorted_by_severity_and_escaped(self):
        proc, out = self.run_cli(REVIEW, {
            "title": "Review of <b>diff</b>",
            "tests": [{"command": "python3 -m unittest", "result": "green", "excerpt": "OK"}],
            "findings": [
                {"severity": "suggestion", "claim": "rename helper"},
                {"severity": "critical", "claim": "<script>alert(1)</script> drops rows", "location": "a.py:3",
                 "scenario": "empty file -> load -> IndexError", "lens": "data-loss", "converged": True},
                {"severity": "medium", "claim": "slow path", "status": "fixed"},
            ],
        })
        self.assertEqual(proc.returncode, 0, proc.stderr)
        page = out.read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("Review of &lt;b&gt;diff&lt;/b&gt;", page)
        self.assertLess(page.index("drops rows"), page.index("slow path"))
        self.assertLess(page.index("slow path"), page.index("rename helper"))
        self.assertIn("--sev:var(--critical)", page)
        self.assertIn("1 critical", page)
        self.assertNotIn("1 medium", page)  # fixed findings are not counted as open

    def test_empty_findings_render_a_clean_result(self):
        proc, out = self.run_cli(REVIEW, {"title": "Clean", "findings": []})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("no open findings", out.read_text(encoding="utf-8"))

    def test_rejects_unknown_severity_without_writing(self):
        proc, out = self.run_cli(REVIEW, {"title": "Bad", "findings": [{"severity": "blocker", "claim": "x"}]})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("severity must be one of", proc.stderr)
        self.assertFalse(out.exists())

    def test_rejects_unknown_test_result(self):
        proc, _ = self.run_cli(REVIEW, {"title": "Bad", "findings": [], "tests": [{"command": "x", "result": "pass"}]})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("result must be one of", proc.stderr)


class PlanRendererTests(RendererTestCase):
    def test_approaches_side_by_side_with_chosen_marked(self):
        proc, out = self.run_cli(PLAN, {
            "title": "Plan: CSV import",
            "spec_path": ".plan-then-ship/SPEC.md",
            "approaches": [
                {"name": "Stream rows", "pros": ["constant memory"], "cons": ["two passes"], "chosen": True},
                {"name": "Load <all>", "summary": "pandas", "cons": ["new dependency"]},
            ],
            "assumptions": ["UTF-8 input"],
        })
        self.assertEqual(proc.returncode, 0, proc.stderr)
        page = out.read_text(encoding="utf-8")
        self.assertEqual(page.count('<section class="card'), 2)
        self.assertEqual(page.count('<section class="card chosen"'), 1)
        self.assertIn("Chosen: Stream rows", page)
        self.assertIn("Load &lt;all&gt;", page)
        self.assertIn(".plan-then-ship/SPEC.md", page)
        self.assertIn("Assumptions awaiting approval", page)

    def test_undecided_plan_says_the_choice_is_pending(self):
        proc, out = self.run_cli(PLAN, {"title": "Plan", "approaches": [{"name": "A"}, {"name": "B"}]})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("No approach chosen yet", out.read_text(encoding="utf-8"))

    def test_rejects_two_chosen_approaches(self):
        proc, out = self.run_cli(PLAN, {"title": "Plan", "approaches": [
            {"name": "A", "chosen": True}, {"name": "B", "chosen": True}]})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("at most one approach", proc.stderr)
        self.assertFalse(out.exists())

    def test_rejects_missing_approaches(self):
        proc, _ = self.run_cli(PLAN, {"title": "Plan", "approaches": []})
        self.assertEqual(proc.returncode, 2)

    def test_rejects_malformed_approach_and_string_lists(self):
        for bad in ({"title": "Plan", "approaches": ["A"]},
                    {"title": "Plan", "approaches": [{"name": "A", "pros": "one string"}]},
                    {"title": "Plan", "approaches": [{"name": "A"}], "acceptance": "x"}):
            proc, _ = self.run_cli(PLAN, bad)
            self.assertEqual(proc.returncode, 2, bad)


if __name__ == "__main__":
    unittest.main()
