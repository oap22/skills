# Skill scenarios and regression record, 2026-10-02

Dated snapshot. Records why `evals/skill-scenarios.json`, `scripts/skill_scenarios.py`, and `skills/skillify/regression.md` exist, what was measured, and what was only inferred. Current counts come from the commands in `AGENTS.md`.

## Sources (fetched 2026-10-01 through a summarizing fetch tool; summaries, not full-text reads)

| Source | Status | What was taken |
|---|---|---|
| Cherny, "I am often wrong" (2026-09-19) | fetched | Redefine problem, approach, and goal when new evidence arrives; unclear success metrics are a common failure. |
| Every transcript, Cherny/Cat interview (2025-10-29) | fetched | Separate review contexts, then agents that filter false positives. Already how `adversarial-review` works; no change made. |
| Shihipar, skills post (2026-03-18, LinkedIn) | fetched | Description is a trigger; gotchas are highest signal; link files for progressive disclosure; measure skill usage. Usage hooks were not adopted (no runtime validation). |
| Context-engineering post (claude.dev) | fetched | Slim instructions, avoid conflicting instructions, progressive disclosure. Vendor claims, not evidence for this repo. |
| Session-management post (2026-04-15) | fetched | Subagents for conclusions only, fresh sessions for new tasks. Informs the reviewer-per-fresh-context step; no change made. |
| "Seeing like an agent" (claude.dev) | fetched | Progressive disclosure, observe what the agent actually uses. Background only. |
| Fable "finding your unknowns" | fetched on retry; not relied on | No change derives from it. |
| X originals | not accessible | Nothing here claims their text. |

## Source to change

| Idea (synthesis) | Change |
|---|---|
| Descriptions are triggers with boundaries | Scenarios assert the boundary cues and quoted triggers a prompt relies on; checker rejects a trigger phrase claimed by two skills. |
| Evidence before claiming done; redefine on new evidence | Scenarios assert skill bodies state the evidence they require (for example verifier plus CI, secret review before publishing). Frontmatter is excluded so a description cannot satisfy it. |
| Learn from retros without self-editing | `regression.md`: fix the cause, pin one scenario with a dated origin, show it fails without the fix. No automatic edits. |
| Gotchas and progressive disclosure | Procedure lives in a linked sibling file, not the skillify entrypoint. |

## Measured vs inferred

Measured: unit tests pass, the real catalog has no trigger collisions, each scenario passes on the real files, a scratch mutation of a real description fails the checker, and an independent reviewer's malformed-input crashes and description-satisfies-evidence hole were reproduced and fixed. Inferred: that this catches future routing regressions, and that the cited advice transfers to this repo. Neither was tested.

## Limits

- Text contract only. It does not show a model routes a prompt correctly or follows a skill; live routing and trajectory evaluation were not run.
- A scenario passing cannot show the instruction is good, only that its cues and evidence phrases are present.
- Trigger-collision checking is catalog-wide, so unrelated skill edits can fail the scenario check.
- Scenarios were curated from existing descriptions and a prior lane-run lesson, not from newly observed misroutes; origin `kind` says which.

## Rebase note

The first push was based on a local `main` whose unpushed history diverged from `origin/main` (equal content, different hashes, plus local-only skills such as `research-survey` and `project-status-doc`). It conflicted. The two commits were cherry-picked onto `origin/main` 3c127df (including PR #7's private-value move), and scenarios referencing local-only skills were dropped or retargeted. Local-only skills can gain scenarios once they land on `origin/main`.
