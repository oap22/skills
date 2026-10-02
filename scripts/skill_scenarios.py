#!/usr/bin/env python3
"""Offline contract check for curated skill scenarios (evals/skill-scenarios.json).

Checks only what text can prove: the scenario file is well formed, every named
skill exists, the descriptions carry the trigger and boundary cues the scenario
relies on, quoted trigger phrases do not collide across skills, and the skill
files state the evidence they require before claiming completion. It does not
route a prompt through a model; live routing and trajectories need a harness run.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_contract import load_catalog  # noqa: E402

SCHEMA_VERSION = 1
KINDS = {"curated", "audit", "retro"}
SCENARIO_KEYS = {"id", "prompt", "expected_skill", "not_skills", "literal_trigger",
                 "description_cues", "evidence", "origin"}
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
QUOTED = re.compile(r'"([^"]+)"')


def trigger_phrases(description):
    """Quoted phrases in a description; these are the user words it claims to match."""
    return [m.lower() for m in QUOTED.findall(description)]


def _is_date(value):
    try:
        return isinstance(value, str) and bool(date.fromisoformat(value)) and len(value) == 10
    except ValueError:
        return False


def _strs(value):
    return isinstance(value, list) and value and all(isinstance(v, str) and v.strip() for v in value)


def _name(value, names):
    return isinstance(value, str) and value in names


def _contains_phrase(prompt, phrase):
    """Whole-word match so a short trigger cannot hit inside an unrelated word."""
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", prompt) is not None


def _bundled(repo, skill, name):
    """Body text of a file inside the skill folder (frontmatter stripped), else None."""
    if not isinstance(name, str):
        return None
    folder = (repo / "skills" / skill).resolve()
    try:
        path = (folder / name).resolve()
        if folder not in path.parents or not path.is_file():
            return None
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    return re.sub(r"\A---\n.*?\n---(?:\n|$)", "", text, count=1, flags=re.S)


def collisions(descriptions):
    """Trigger phrases claimed by more than one skill."""
    owners = {}
    for skill, description in descriptions.items():
        for phrase in trigger_phrases(description):
            owners.setdefault(phrase, set()).add(skill)
    return {p: sorted(s) for p, s in owners.items() if len(s) > 1}


def check(repo, path=None):
    """Return a list of problem strings; empty means the contract holds."""
    repo = Path(repo)
    path = Path(path) if path else repo / "evals" / "skill-scenarios.json"
    descriptions = {name: desc for name, desc, _ in load_catalog(repo)}
    problems = [f"trigger phrase {p!r} claimed by {', '.join(s)}"
                for p, s in sorted(collisions(descriptions).items())]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return problems + [f"{path.name}: {exc}"]
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        return problems + [f"{path.name}: schema_version must be {SCHEMA_VERSION}"]
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return problems + [f"{path.name}: scenarios must be a nonempty list"]
    seen = set()
    for index, s in enumerate(scenarios):
        sid = s.get("id") if isinstance(s, dict) else None
        label = f"scenario {sid if isinstance(sid, str) and sid else index}"
        if not isinstance(s, dict):
            problems.append(f"{label}: must be an object")
            continue
        if extra := set(s) - SCENARIO_KEYS:
            problems.append(f"{label}: unknown keys {sorted(extra)}")
        if not isinstance(sid, str) or not ID.fullmatch(sid):
            problems.append(f"{label}: id must be kebab-case")
        elif sid in seen:
            problems.append(f"{label}: duplicate id")
        else:
            seen.add(sid)
        prompt, expected = s.get("prompt"), s.get("expected_skill")
        not_skills = s.get("not_skills", [])
        if not isinstance(prompt, str) or not prompt.strip():
            problems.append(f"{label}: prompt must be a nonempty string")
            prompt = ""
        if expected is not None and not _name(expected, descriptions):
            problems.append(f"{label}: expected_skill {expected!r} is not in the catalog")
        if expected is None and not not_skills:
            problems.append(f"{label}: a no-skill scenario must name not_skills")
        if not isinstance(not_skills, list) or not all(_name(n, descriptions) for n in not_skills):
            problems.append(f"{label}: not_skills must list catalog skills")
            not_skills = []
        if expected is not None and expected in not_skills:
            problems.append(f"{label}: expected_skill also listed in not_skills")
        origin = s.get("origin")
        if (not isinstance(origin, dict) or origin.get("kind") not in KINDS or
                not isinstance(origin.get("ref"), str) or not origin["ref"].strip() or
                not _is_date(origin.get("observed"))):
            problems.append(f"{label}: origin needs kind {sorted(KINDS)}, ref, and observed date")
        elif origin["kind"] == "retro" and not origin["ref"].startswith(("http", "retro:")):
            problems.append(f"{label}: retro origin ref must be a URL or retro:<id>")
        cues = s.get("description_cues", [])
        if not isinstance(cues, list):
            problems.append(f"{label}: description_cues must be a list")
            cues = []
        elif expected is not None and not cues:
            problems.append(f"{label}: needs description_cues for the expected skill")
        for cue in cues:
            skill, contains = (cue.get("skill"), cue.get("contains")) if isinstance(cue, dict) else (None, None)
            if not _name(skill, descriptions) or not isinstance(contains, str) or not contains:
                problems.append(f"{label}: bad description cue {cue!r}")
            elif contains.lower() not in descriptions[skill].lower():
                problems.append(f"{label}: description of {skill} lacks {contains!r}")
        literal = s.get("literal_trigger", False)
        if not isinstance(literal, bool):
            problems.append(f"{label}: literal_trigger must be true or false")
        elif literal:
            hits = {n for n, d in descriptions.items()
                    if any(_contains_phrase(prompt.lower(), p) for p in trigger_phrases(d))}
            if not _name(expected, descriptions) or expected not in hits:
                problems.append(f"{label}: prompt contains no quoted trigger of {expected!r}")
            for wrong in sorted(hits & set(not_skills)):
                problems.append(f"{label}: prompt matches a trigger of excluded skill {wrong}")
        evidence = s.get("evidence", [])
        if not isinstance(evidence, list):
            problems.append(f"{label}: evidence must be a list")
            evidence = []
        for item in evidence:
            skill = item.get("skill") if isinstance(item, dict) else None
            phrases = item.get("contains") if isinstance(item, dict) else None
            if not _name(skill, descriptions) or not _strs(phrases):
                problems.append(f"{label}: bad evidence item {item!r}")
                continue
            file = item.get("file", "SKILL.md")
            text = _bundled(repo, skill, file)
            if text is None:
                problems.append(f"{label}: {skill}/{file} is not a bundled file")
                continue
            for phrase in phrases:
                if phrase.lower() not in text.lower():
                    problems.append(f"{label}: {skill}/{file} lacks evidence contract {phrase!r}")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scenarios")
    args = parser.parse_args(argv)
    try:
        problems = check(args.repo, args.scenarios)
    except ValueError as exc:
        problems = [str(exc)]
    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print("skill scenarios: offline contract holds (live routing not evaluated)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
