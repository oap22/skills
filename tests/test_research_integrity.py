"""CLI integrity checks for research records and trajectories.

These tests use only temporary directories and invoke the public helper CLI.
They intentionally cover records that look plausible but must not be citable.
"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/research-loop/log_run.py"
SHA = "a" * 40
EVAL_HASH = "b" * 64


class ResearchIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def cli(self, *args, cwd=None, timeout=10):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            cwd=cwd or self.root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def make_run(self, name="2026-09-05-run-a", *, git=True, eval_hash=EVAL_HASH,
                 n_examples=20, applicable=True):
        run = self.root / name
        run.mkdir()
        (run / "run.json").write_text(json.dumps({
            "run_id": name,
            "name": "run-a",
            "command": ["python3", "experiment.py"],
            "started_at": "2026-09-05T00:00:00+00:00",
            "finished_at": "2026-09-05T00:01:00+00:00",
            "duration_seconds": 60.0,
            "exit_code": 0,
            "git": ({
                "available": True,
                "sha": SHA,
                "branch": "main",
                "dirty": False,
            } if git else {"available": False}),
        }))
        if applicable:
            metrics = {
                "accuracy": 0.7,
                "seed": 42,
                "n_examples": n_examples,
                "eval_set": "held-out-v1",
                "eval_set_sha256": eval_hash,
            }
        else:
            metrics = {
                "accuracy": 0.7,
                "seed": "not-applicable: deterministic",
                "n_examples": "not-applicable: deterministic",
                "eval_set": "not-applicable: deterministic",
                "eval_set_sha256": "not-applicable: deterministic",
            }
        (run / "metrics.json").write_text(json.dumps(metrics))
        (run / "notes.md").write_text(
            "# Run\n\nQuestion and answer.\n\n"
            "## Verification\nCompared against the control.\n\n"
            "## Caveats\nStructural fixture only.\n"
        )
        return run

    def trajectory(self, loop, run, round_number, **extra):
        args = [
            "trajectory", loop, "--round", round_number, "--run-dir", run,
            "--primary", extra.pop("primary", "0.7"),
            "--noise-floor", extra.pop("noise_floor", "0.01"),
            "--secondary", extra.pop("secondary", "0.6"),
            "--gpu-hours", extra.pop("gpu_hours", "1"),
            "--dollars", extra.pop("dollars", "1"),
            "--human-interventions", extra.pop("human_interventions", "0"),
        ]
        for key, value in extra.items():
            args.extend([f"--{key.replace('_', '-')}", value])
        return self.cli(*args)

    def test_check_rejects_missing_git_provenance_and_bad_typed_metadata(self):
        run = self.make_run(git=False)
        result = self.cli("check", run)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required Git provenance", result.stdout)

        run = self.make_run("2026-09-05-bad-metadata", eval_hash="not-a-sha")
        result = self.cli("check", run)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("64 hex", result.stdout)

    def test_check_accepts_explicit_non_dataset_metadata(self):
        run = self.make_run(applicable=False)
        result = self.cli("check", run)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_rejects_symlinked_citation_file(self):
        run = self.make_run()
        old = self.root / "old-metrics.json"
        old.write_text((run / "metrics.json").read_text())
        (run / "metrics.json").unlink()
        (run / "metrics.json").symlink_to(old)
        result = self.cli("check", run)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be a regular file", result.stdout)

    def test_trajectory_requires_real_round_zero_and_completed_run(self):
        run = self.make_run()
        loop = self.root / "loop"
        result = self.trajectory(loop, run, 1)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("first trajectory round must be round 0", result.stderr)
        self.assertFalse((loop / "trajectory.json").exists())

        result = self.trajectory(loop, self.root / "missing", 0)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a run directory", result.stderr)

        result = self.trajectory(loop, run, 0)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads((loop / "trajectory.json").read_text())
        self.assertEqual(payload["rounds"][0]["run_id"], run.name)
        self.assertIsNone(payload["rounds"][0]["parent_run_id"])

    def test_trajectory_links_parent_and_rejects_eval_identity_change(self):
        run0 = self.make_run()
        run1 = self.make_run("2026-09-05-run-b")
        loop = self.root / "loop"
        self.assertEqual(self.trajectory(loop, run0, 0).returncode, 0)
        result = self.trajectory(loop, run1, 1)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload_before = (loop / "trajectory.json").read_bytes()

        run2 = self.make_run("2026-09-05-run-c", eval_hash="c" * 64)
        result = self.trajectory(loop, run2, 2)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("eval identity changed", result.stderr)
        self.assertEqual((loop / "trajectory.json").read_bytes(), payload_before)

    def test_trajectory_requires_explicit_loop_metadata(self):
        run = self.make_run()
        result = self.cli(
            "trajectory", self.root / "loop", "--round", "0", "--run-dir", run,
            "--primary", "0.7", "--noise-floor", "0.01", "--secondary", "0.6",
            "--gpu-hours", "1", "--human-interventions", "0",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--dollars", result.stderr)

    def test_metrics_concurrent_updates_are_not_lost(self):
        run = self.root / "metrics-run"
        run.mkdir()
        (run / "metrics.json").write_text("{}")
        processes = [
            subprocess.Popen(
                [sys.executable, str(SCRIPT), "metrics", run, "--set", f"k{i}={i}"],
                cwd=self.root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            for i in range(8)
        ]
        failures = []
        for process in processes:
            _, stderr = process.communicate()
            failures.append((process.returncode, stderr))
        self.assertTrue(all(code == 0 for code, _ in failures), failures)
        metrics = json.loads((run / "metrics.json").read_text())
        self.assertEqual({f"k{i}" for i in range(8)}, set(metrics))
        self.assertFalse((run / ".metrics.json.lock").exists())

    def test_metrics_does_not_hijack_existing_lock(self):
        run = self.root / "locked-run"
        run.mkdir()
        (run / "metrics.json").write_text("{}")
        lock = run / ".metrics.json.lock"
        lock.write_text("owner=unknown")
        result = self.cli("metrics", run, "--set", "new=1", timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to remove", result.stderr)
        self.assertEqual(lock.read_text(), "owner=unknown")
        self.assertEqual((run / "metrics.json").read_text(), "{}")


if __name__ == "__main__":
    unittest.main()
