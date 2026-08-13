---
name: turing
description: Working context for the Turing repo and the Turing desktop app. Load whenever Owen says he is "working in Turing", "in the Turing repo", doing research dev in Turing, or has the Turing desktop open. Makes the rule explicit — research work in Turing runs through /research-interview and /research-loop, never ad-hoc — and defines the data contract (metrics.jsonl, trajectory.json, plots) that makes experiment output show up live in the desktop app's panes.
---

# Turing

Turing (`~/Developer/active/Turing`, github `oap22/Turing`) is Owen's autonomous-research-agent project, and **the Turing desktop app** is his operator surface for it: a Tauri tiling app (issue #382, `desktop/`) with terminals, live metric charts, a flywheel timeline, an image viewer, and an agent viewer. When Owen says you are working in Turing, both of these rules bind.

## Rule 1 — research work uses the research workflows. Always.

Turing is where Owen does research development. If the session is research-shaped — an experiment, a training run, a benchmark, an ablation, a flywheel round, "let's test whether X" — then:

- **No current brief? Run `/research-interview` first.** Briefs live in `research/briefs/`; a brief with `status: agreed` is the contract. Do not start experiment code from a vibe.
- **Every experiment runs under `/research-loop`.** Ground → design gate → cost gate → run → falsify → log. Its `conventions.md` owns the results-directory format, `JOURNAL.md`, and `DEAD-ENDS.md`.
- **Heavy jobs go to ROSIE via `rosie-run`.** The Mac orchestrates; the cluster computes.

Ordinary feature work on Turing's own code (gateway, desktop app, tooling) is normal engineering and does **not** use the research loop — but a session that produces a number Owen might trust later does.

## Rule 2 — expose your data where the desktop renders it

Everything the desktop app shows is a plain file. Write to these paths and Owen literally watches your work live; skip them and your run is invisible.

| You produce | Write to | Desktop pane |
|---|---|---|
| Live training/eval metrics | `research/results/<run>/metrics.jsonl` — **append one JSON object per step** | metrics (charts every numeric field, live) |
| Final summary numbers | `research/results/<run>/metrics.json` | metrics (static) — required by research-loop conventions |
| Flywheel / loop rounds | `research/results/loop-<slug>/trajectory.json` (+ `round-NN/round.json`) | flywheel timeline |
| Plots / figures | `research/results/<run>/*.svg` or `*.png` | images (auto-selects newest) |
| Remote job metrics, live (Rosie or any ssh host) | `ssh <HOST> 'tail -n +1 -F <run>/metrics.jsonl' \| tee -a research/results/<run>/metrics.jsonl` (desktop runner `ssh-follow-metrics` pre-types this) | metrics |
| Remote plots/assets, live | rsync loop via desktop runner `ssh-pull-assets` into `research/results/` | images + metrics |

### metrics.jsonl line contract

```json
{"step": 12, "total_steps": 300, "ts": 1755100000, "loss": 0.412, "accuracy": 0.83, "lr": 0.0002}
```

- Every **numeric** field becomes a chart series automatically — add whatever you measure.
- `step` is the x-axis (falls back to line index). `total_steps` enables the ETA strip — include it. `ts` (epoch s or ms) drives the steps/sec rate.
- Non-numeric fields are ignored; malformed lines are skipped. Append, never rewrite.

### Driving the operator's view

Write `research/results/.viewer.json` to point Owen's metrics pane at what he should look at — `{"series": "accuracy", "runs": ["run-42"], "titles": {"accuracy": "held-out accuracy — run 42"}}`. `series` switches the visible chart tab, `runs` selects/overlays runs, `titles` renames chart headings. Owen can edit the same file manually; unknown or malformed keys are ignored.

### Reading it back

You can read everything the desktop shows: the JSONL/JSON files above, the SVG/PNG plots (open them — you can see images), and other agents' transcripts (`~/.claude/projects`, `~/.codex/sessions`). When Owen says "look at the current run", it's `research/results/` — same files his charts are drawn from.

## Orientation

- Repo conventions: `CLAUDE.md` at the Turing repo root (issue-claiming, branch naming, PR tiers, GitNexus).
- Research state: `research/HANDOFF.md`, `research/JOURNAL.md`, the agreed brief in `research/briefs/`.
- Desktop app usage/keymap: `desktop/README.md` (mod=⌘, ⌘P launcher, workspaces 1–5).
- The gateway panes (queue/chat/obs) talk to the dormant coordinator stack — offline is their normal state until that wakes.
