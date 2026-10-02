"""Scenario contract: the real repo passes, and each failure mode is detected."""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(os.environ.get('SKILLS_TEST_ROOT', Path(__file__).resolve().parents[1]))
spec = importlib.util.spec_from_file_location('skill_scenarios', ROOT / 'scripts/skill_scenarios.py')
scen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scen)


def skill(name, description, body='# Body\nDo the thing.\n'):
    return f'---\nname: {name}\ndescription: {json.dumps(description)}\n---\n{body}'


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.add('alpha', 'Review diffs. Use for "review this diff". Not for beta.', '# A\nReport a concrete failure scenario.\n')
        self.add('beta', 'Ship releases. Use for "cut a release". Reviews are alpha.')
        (self.repo / 'manifest.json').write_text(json.dumps({'skills': {'alpha': ['codex'], 'beta': ['codex']}}))
        (self.repo / 'evals').mkdir()
        self.scenario = {
            'id': 'review-not-ship', 'prompt': 'please review this diff', 'expected_skill': 'alpha',
            'not_skills': ['beta'], 'literal_trigger': True,
            'description_cues': [{'skill': 'alpha', 'contains': 'Not for beta'}],
            'evidence': [{'skill': 'alpha', 'contains': ['concrete failure scenario']}],
            'origin': {'kind': 'retro', 'ref': 'retro:2026-10-01-misroute', 'observed': '2026-10-01'},
        }

    def add(self, name, description, body='# Body\nDo the thing.\n'):
        folder = self.repo / 'skills' / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'SKILL.md').write_text(skill(name, description, body))

    def problems(self, *scenarios):
        (self.repo / 'evals' / 'skill-scenarios.json').write_text(
            json.dumps({'schema_version': 1, 'scenarios': list(scenarios)}))
        return scen.check(self.repo)

    def mutate(self, **changes):
        s = copy.deepcopy(self.scenario)
        for key, value in changes.items():
            if value is None:
                s.pop(key, None)
            else:
                s[key] = value
        return self.problems(s)

    def assertProblem(self, problems, fragment):
        self.assertTrue(any(fragment in p for p in problems), problems)

    def test_valid_scenario_passes(self):
        self.assertEqual(self.problems(self.scenario), [])

    def test_repository_scenarios_hold(self):
        self.assertEqual(scen.check(ROOT), [])

    def test_cli_reports_failure_with_nonzero_exit(self):
        self.problems(dict(self.scenario, expected_skill='ghost'))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(scen.main(['--repo', str(self.repo)]), 1)
        self.assertIn('ghost', err.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(scen.main(['--repo', str(ROOT)]), 0)

    def test_missing_scenario_file_and_bad_schema(self):
        self.assertProblem(scen.check(self.repo), 'skill-scenarios.json')
        (self.repo / 'evals' / 'skill-scenarios.json').write_text('{"schema_version": 2, "scenarios": []}')
        self.assertProblem(scen.check(self.repo), 'schema_version')

    def test_unknown_expected_skill(self):
        self.assertProblem(self.mutate(expected_skill='ghost'), 'not in the catalog')

    def test_missing_description_cue_is_detected(self):
        cue = [{'skill': 'alpha', 'contains': 'Not for gamma'}]
        self.assertProblem(self.mutate(description_cues=cue), "lacks 'Not for gamma'")
        self.assertProblem(self.mutate(description_cues=None), 'needs description_cues')

    def test_missing_evidence_contract_is_detected(self):
        ev = [{'skill': 'alpha', 'contains': ['independent verifier']}]
        self.assertProblem(self.mutate(evidence=ev), 'lacks evidence contract')
        ev = [{'skill': 'alpha', 'file': '../beta/SKILL.md', 'contains': ['Ship']}]
        self.assertProblem(self.mutate(evidence=ev), 'not a bundled file')
        ev = [{'skill': 'alpha', 'file': 'missing.md', 'contains': ['x']}]
        self.assertProblem(self.mutate(evidence=ev), 'not a bundled file')

    def test_literal_trigger_must_hit_expected_and_miss_excluded(self):
        self.assertProblem(self.mutate(prompt='please cut a release'), "no quoted trigger of 'alpha'")
        both = 'review this diff then cut a release'
        self.assertProblem(self.mutate(prompt=both), 'excluded skill beta')

    def test_no_skill_scenario_needs_exclusions(self):
        s = self.mutate(expected_skill=None, not_skills=[], description_cues=[], literal_trigger=None)
        self.assertProblem(s, 'must name not_skills')
        self.assertEqual(self.mutate(expected_skill=None, description_cues=[], literal_trigger=None), [])

    def test_provenance_is_required_and_retro_needs_a_ref(self):
        self.assertProblem(self.mutate(origin=None), 'origin needs')
        bad = {'kind': 'retro', 'ref': 'a hunch', 'observed': '2026-10-01'}
        self.assertProblem(self.mutate(origin=bad), 'retro origin ref')
        self.assertProblem(self.mutate(origin={'kind': 'retro', 'ref': 'retro:1', 'observed': 'soon'}), 'origin needs')

    def test_duplicate_ids_and_unknown_keys(self):
        self.assertProblem(self.problems(self.scenario, self.scenario), 'duplicate id')
        self.assertProblem(self.mutate(extra=1), 'unknown keys')

    def test_trigger_collision_between_skills_is_detected(self):
        self.add('beta', 'Ship releases. Use for "review this diff" or "cut a release".')
        self.assertProblem(self.problems(self.scenario), "'review this diff' claimed by alpha, beta")

    def test_malformed_shapes_return_problems_instead_of_crashing(self):
        for key, value in [('id', ['a']), ('expected_skill', ['a']), ('not_skills', [['a']]),
                           ('description_cues', None), ('description_cues', 5), ('evidence', None),
                           ('evidence', 3), ('literal_trigger', 'true'), ('prompt', 7),
                           ('description_cues', [{'skill': ['a'], 'contains': 'x'}, 'x']),
                           ('evidence', [{'skill': ['a'], 'contains': ['x']}, 4]),
                           ('evidence', [{'skill': 'alpha', 'file': 5, 'contains': ['x']}]),
                           ('evidence', [{'skill': 'alpha', 'file': 'a\x00b', 'contains': ['x']}]),
                           ('origin', {'kind': 'retro', 'ref': 'retro:1', 'observed': '2026-99-99'})]:
            with self.subTest(key=key, value=value):
                s = dict(self.scenario, **{key: value})
                self.assertTrue(self.problems(s))

    def test_evidence_must_be_in_the_body_not_the_description(self):
        self.add('alpha', 'Review diffs, with an independent verifier. Use for "review this diff". Not for beta.')
        ev = [{'skill': 'alpha', 'contains': ['independent verifier']}]
        self.assertProblem(self.mutate(evidence=ev, description_cues=[{'skill': 'alpha', 'contains': 'Not for beta'}]),
                           'lacks evidence contract')

    def test_literal_trigger_matches_whole_words_only(self):
        self.add('alpha', 'Review diffs. Use for "review". Not for beta.', '# A\nReport a concrete failure scenario.\n')
        self.assertProblem(self.mutate(prompt='please preview this'), "no quoted trigger of 'alpha'")
        self.assertEqual(self.mutate(prompt='please review this'), [])


if __name__ == '__main__':
    unittest.main()
