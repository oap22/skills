---
name: run-spec
description: "Freeze a designed ML training run into an agreed brief, a config file, and one launch command, with every value sourced. Use after run-viz, or for \"write the run spec\", \"lock this run\". Interview is run-grill; tuning is run-viz; executing and logging is research-loop."
---

# Run Spec

Turn the draft brief and `choices.json` into a run that research-loop can execute without a question.

## Steps

1. Read the brief and `<slug>.choices.json`. A missing input sends Owen back to `run-grill` or `run-viz`.
2. Write the config in the repo's existing format (YAML, Hydra, argparse flags). Do not invent a new one.
3. Add a `## Spec` section to the brief: config path, launch command for the chosen target (local command, or a job script modeled on the repo's existing ones for that scheduler), expected runtime and cost, and the git SHA to run from.
4. **Check.** No `?`, TODO, or open question that blocks launch. Every number traces to the brief, the choices, or the repo. Config values match the brief.
5. Restate the run in five lines. On Owen's approval, set `status: agreed` and hand off to `research-loop`, plus the dispatch skill for that target if one exists.

## Rules

- Do not launch anything. Launching belongs to research-loop or the target's dispatch skill.
- A change after agreement goes in the brief's `## Deviations`; it never edits the spec in place.

## Gotchas

None recorded yet. Add one here when a run fails a new way.
