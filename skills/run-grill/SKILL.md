---
name: run-grill
description: "Grill Owen one question at a time about an ML training run until nothing is ambiguous, then write a draft run brief. First step whenever a training run is being designed: \"grill me on this run\", \"I want to train X\", \"design a run\". Next steps are run-viz (see and tune it) and run-spec (freeze it); executing is research-loop."
---

# Run Grill

Remove every ambiguity from a planned training run before any compute is spent.

## Steps

1. **Read first.** Read the repo (config, train script, data loader), `research/`, past runs in the results root, and any brief in `research/briefs/`. Open with what you already believe and ask what is wrong.
2. **Grill.** One question per message; use the structured question tool with 2–4 options when the answers are enumerable. Each question follows from the last answer. Pull every hedge ("probably", "should be fine"). Attack weak baselines, gameable metrics, and leaks now. Do not stop while any "Must be pinned" item, any answer that could mean two things, or any hedge is open; Owen's fatigue or a long interview is not a reason to stop. Before closing, re-scan the whole brief for one more ambiguity and ask about it.
3. **Write as you go** to `research/briefs/YYYY-MM-DD-<slug>.md` with `status: draft`.
4. **Close.** Restate the whole run. If Owen changes nothing, hand off to `run-viz`.

## Must be pinned

Each item gets a value or a path. An open question is allowed only when no answer is possible before the run, and it must name the run step that answers it.

- **Question**: what the run decides, and the result that kills the idea
- **Data**: paths, splits, held-out set, leakage risks, preprocessing
- **Model**: architecture, init or checkpoint, size
- **Objective**: loss, metric, the baseline it must beat, smallest delta that matters, seeds
- **Optimization**: optimizer, LR and schedule, batch, epochs or steps, precision
- **Compute target**: any machine or cluster. Detect it from the repo (job scripts such as `*.sbatch` or `*.pbs`, cluster facts files, Dockerfiles, launch configs) and the local hardware; ask only which one. Then GPUs, wall-clock, job limits, budget; do the arithmetic aloud
- **Stop and fail rules**: early stop, abort triggers, what happens if it diverges
- **Outputs**: checkpoints, logs, where results land

## Rules

- Never ask what the repo or past runs answer.
- No load-bearing word stays undefined: "better", "the baseline", and "the model" each get a number, name, or path.
- The design is Owen's. Propose and challenge; do not substitute.

## Gotchas

None recorded yet. Add one here when a run fails a new way.
