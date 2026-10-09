---
name: run-viz
description: "Build one interactive HTML page for a planned ML training run that teaches what will happen, shows Owen's real code, lets him tune knobs, shows what each change does, and collects his choices. Use after run-grill, or for \"visualize this run\", \"show me what this run does\", \"help me pick the hyperparameters\". Interview is run-grill; freezing the spec is run-spec; live or past run plots are turing."
---

# Run Viz

Make the planned run visible and teachable, then collect Owen's choices.

## Input

The draft brief in `research/briefs/` from `run-grill`. No brief: run `run-grill` first.

## Page sections

1. **Pipeline**: data → model → loss → optimizer → eval, with the run's real numbers.
2. **Learn**: per stage, 2–3 plain sentences plus the real snippet from the repo with `file:line`. No generic code.
3. **Knobs**: one control per open or tunable choice from the brief, each with a one-line "why it matters".
4. **Difference**: current vs proposed, side by side, updated live.
5. **Decide**: lock each knob, add a note, export `choices.json`.

## Show only what is computable

- Exact: LR schedule curve, steps, effective batch, samples seen, memory estimate, runtime and cost, split sizes, class balance, augmented real samples.
- Evidence: overlays of past runs from the results root.
- Never draw a predicted loss curve. Label any theory-based claim "expected", never "measured".

## Delivery

Publish as a private artifact when the harness can, with page state Claude can read back. Otherwise write `research/viz/<slug>.html` with a Copy JSON button and ask Owen to paste the result. Save the choices beside the brief as `<slug>.choices.json`, then hand off to `run-spec`.

## Gotchas

None recorded yet. Add one here when a run fails a new way.
