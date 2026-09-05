"""Behavior tests in temporary directories; never touch real harnesses or jobs."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('SKILLS_TEST_ROOT', Path(__file__).resolve().parents[1]))

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

installer = module('installer', ROOT / 'install.py')
logger = module('logger', ROOT / 'skills/research-loop/log_run.py')

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / 'repo'
        self.folder = self.repo / 'skills' / 'alpha'
        self.folder.mkdir(parents=True)
        (self.folder / 'SKILL.md').write_text('---\nname: alpha\ndescription: A useful test skill.\n---\n# Alpha\nDoes something specific.\n')
        self.manifest({'alpha': ['codex']})
        self.home = self.root / 'harness'
        self.home.mkdir()
        self.target = self.home / 'skills'
        self.target.mkdir()
        self.addCleanup(patch.stopall)
        patch.object(installer, 'REPO', self.repo).start()
        patch.object(installer, 'TARGETS', {'codex': (self.home, 'skills')}).start()

    def manifest(self, skills):
        (self.repo / 'manifest.json').write_text(json.dumps({'skills': skills}))

    def run_installer(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return installer.main(list(args))

    def test_install_idempotence_and_owned_prune(self):
        self.assertEqual(self.run_installer(), 0)
        link = self.target / 'alpha'
        self.assertEqual(link.resolve(), self.folder)
        first = link.lstat().st_mtime_ns
        self.assertEqual(self.run_installer(), 0)
        self.assertEqual(link.lstat().st_mtime_ns, first)
        stale = self.target / 'old'
        stale.symlink_to(os.path.relpath(self.repo / 'skills' / 'old', self.target))
        self.assertEqual(self.run_installer(), 0)
        self.assertFalse(stale.is_symlink())

    def test_invalid_manifest_never_prunes_or_installs(self):
        stale = self.target / 'old'
        stale.symlink_to(self.repo / 'skills' / 'old')
        for payload in [{}, {'skills': []}, {'skills': {'../escape': ['codex']}}, {'skills': {'alpha': 'codex'}}]:
            (self.repo / 'manifest.json').write_text(json.dumps(payload))
            self.assertEqual(self.run_installer(), 1)
            self.assertTrue(stale.is_symlink())
            self.assertFalse((self.target / 'alpha').exists())

    def test_invalid_frontmatter_fails_before_mutation(self):
        (self.folder / 'SKILL.md').write_text('---\nname: alpha\ndescription: "unfinished\n---\nBody\n')
        self.assertEqual(self.run_installer(), 1)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_foreign_symlink_preserved(self):
        link = self.target / 'alpha'
        link.symlink_to(self.root / 'foreign')
        self.assertEqual(self.run_installer(), 1)
        self.assertEqual(os.readlink(link), str(self.root / 'foreign'))

    def test_real_directory_collision_prevents_all_mutations(self):
        (self.target / 'alpha').mkdir()
        old = self.target / 'old'
        old.symlink_to(self.repo / 'skills' / 'old')
        self.assertEqual(self.run_installer(), 1)
        self.assertTrue(old.is_symlink())

    def test_dry_run_and_check_do_not_write(self):
        self.assertEqual(self.run_installer('--dry-run'), 0)
        self.assertEqual(self.run_installer('--check'), 0)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_worktree_apply_refused(self):
        (self.repo / '.git').write_text('gitdir: /some/worktree\n')
        self.assertEqual(self.run_installer(), 1)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_duplicate_json_rejected(self):
        (self.repo / 'manifest.json').write_text('{"skills":{"alpha":["codex"],"alpha":[]}}')
        self.assertEqual(self.run_installer('--check'), 1)

    def test_manifest_removal_deactivates_without_deleting_source(self):
        self.assertEqual(self.run_installer(), 0)
        self.manifest({})
        self.assertEqual(self.run_installer(), 0)
        self.assertFalse((self.target / 'alpha').is_symlink())
        self.assertTrue((self.folder / 'SKILL.md').is_file())

class LoggerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.results = self.root / 'results'
        self.script = ROOT / 'skills/research-loop/log_run.py'

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.script), *map(str, args)], cwd=self.root, capture_output=True, text=True, timeout=30)

    def record(self):
        directory = self.root / 'fixture'
        directory.mkdir()
        (directory / 'run.json').write_text(json.dumps({'exit_code': 0, 'finished_at':'2026-09-05T00:00:00Z', 'git':{'sha':'abc'}}))
        (directory / 'metrics.json').write_text(json.dumps({'accuracy':.7,'seed':42,'n_examples':20,'eval_set':'test','eval_set_sha256':'abc'}))
        (directory / 'notes.md').write_text('# Run\nQuestion and answer.\n## Verification\nCompared the control on 20 examples.\n## Caveats\nOne dataset.\n')
        return directory

    def test_valid_record_and_incomplete_records(self):
        directory = self.record()
        self.assertEqual(self.cli('check',directory).returncode, 0)
        for invalid in ['{}', '[]', '{"seed":NaN}', '{"seed":1e309}', 'bad-json']:
            (directory / 'metrics.json').write_text(invalid)
            self.assertNotEqual(self.cli('check',directory).returncode, 0, invalid)

    def test_verification_section_required(self):
        directory = self.record()
        (directory / 'notes.md').write_text('Everything went well.')
        self.assertNotEqual(self.cli('check',directory).returncode, 0)

    def test_null_exit_not_success(self):
        directory = self.record()
        (directory / 'run.json').write_text('{"exit_code":null,"finished_at":"today"}')
        self.assertNotEqual(self.cli('check',directory).returncode, 0)

    def test_run_exports_output_path_and_preserves_stale_metrics(self):
        old = self.root / 'metrics.json'
        old.write_text('{"old":true}')
        code = 'import os,pathlib; pathlib.Path(os.environ["RESEARCH_RUN_DIR"],"metrics.json").write_text("{\\"fresh\\":true}"); print("finished")'
        result = self.cli('--results-dir',self.results,'run','--name','smoke','--',sys.executable,'-c',code)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(old.read_text(),'{"old":true}')
        directory = next(self.results.iterdir())
        self.assertEqual(json.loads((directory/'metrics.json').read_text()),{'fresh':True})
        self.assertIn('finished',(directory/'stdout.log').read_text())
        self.assertEqual(json.loads((directory/'run.json').read_text())['exit_code'],0)

    def test_bare_run_does_not_steal_previous_metrics(self):
        old = self.root / 'metrics.json'
        old.write_text('{"old":true}')
        result = self.cli('--results-dir',self.results,'run','--name','empty','--',sys.executable,'-c','print("no metrics")')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(old.exists())
        self.assertFalse((next(self.results.iterdir())/'metrics.json').exists())

    def test_launch_failure_is_recorded(self):
        result = self.cli('--results-dir',self.results,'run','--name','missing','--','/definitely/missing/command')
        self.assertEqual(result.returncode,127)
        record=json.loads((next(self.results.iterdir())/'run.json').read_text())
        self.assertEqual(record['exit_code'],127)
        self.assertIn('finished_at',record)

    def test_slug_cannot_escape_results_root(self):
        result = self.cli('--results-dir',self.results,'run','--name','../../escaped','--',sys.executable,'-c','pass')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(list(self.results.iterdir()),[])

    def test_directory_allocation_is_reserved(self):
        first=logger.allocate_dir('same',self.results)
        second=logger.allocate_dir('same',self.results)
        self.assertNotEqual(first,second)
        self.assertTrue(first.is_dir())
        self.assertTrue(second.is_dir())

    def test_trajectory_preserves_round_history(self):
        loop=self.root/'loop'
        def add(n,primary):
            return self.cli('trajectory',loop,'--round',n,'--run-id',f'run-{n}','--primary',primary,'--noise-floor','.01','--human-interventions','0')
        self.assertEqual(add(0,.5).returncode,0)
        self.assertEqual(add(1,.6).returncode,0)
        before=(loop/'trajectory.json').read_bytes()
        self.assertNotEqual(add(0,.9).returncode,0)
        self.assertEqual((loop/'trajectory.json').read_bytes(),before)
        self.assertNotEqual(add(2,'nan').returncode,0)
        self.assertEqual((loop/'trajectory.json').read_bytes(),before)

    def test_metrics_reject_nonfinite_without_overwriting(self):
        directory=self.record()
        before=(directory/'metrics.json').read_bytes()
        self.assertNotEqual(self.cli('metrics',directory,'--set','accuracy=nan').returncode,0)
        self.assertEqual((directory/'metrics.json').read_bytes(),before)


class SlurmTemplateTests(unittest.TestCase):
    def execute_array(self, index):
        import re
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root/'bin'
            binary.mkdir()
            (binary/'module').write_text('#!/bin/sh\nexit 0\n')
            (binary/'module').chmod(0o755)
            (binary/'python3').write_text(f'#!{sys.executable}\nimport json,os,sys\nopen(os.environ["ARGS_FILE"],"w").write(json.dumps(sys.argv[1:]))\n')
            (binary/'python3').chmod(0o755)
            config = root/'config with spaces.yaml'
            config.write_text('seed: 42\n')
            (root/'sweep-configs.tsv').write_text('42\tconfig with spaces.yaml\n')
            text=(ROOT/'skills/rosie-run/templates/array.sbatch').read_text()
            text=re.sub(r'<[A-Za-z][^<>\n]*>', 'sample', text)
            script=root/'array.sh'
            script.write_text(text)
            out=root/'args.json'
            result=subprocess.run(['bash',str(script)],cwd=root,env={**os.environ,'PATH':str(binary)+os.pathsep+os.environ['PATH'],'SLURM_SUBMIT_DIR':str(root),'SLURM_ARRAY_TASK_ID':str(index),'SLURM_ARRAY_JOB_ID':'123','ARGS_FILE':str(out)},capture_output=True,text=True)
            return result, json.loads(out.read_text()) if out.exists() else None

    def test_array_keeps_seed_separate_from_config_path(self):
        result,args=self.execute_array(0)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(args[args.index('--config')+1],'config with spaces.yaml')
        self.assertEqual(args[args.index('--seed')+1],'42')

    def test_missing_array_row_never_launches_work(self):
        result,args=self.execute_array(1)
        self.assertNotEqual(result.returncode,0)
        self.assertIsNone(args)

if __name__ == '__main__':
    unittest.main()
