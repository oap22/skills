# TODO

Open changes from the 2026-09-24 review of skills against the claude.dev skills post ("Lessons from building Claude Code: How we use skills"; summary in vault note "Using Claude Well").

## Gotchas sections

- [x] **Give every skill a `## Gotchas` heading.** None has one today. Many already have `## Environment` or `## Rules` sections doing the same job; rename or regroup those rather than writing new content. The post calls Gotchas the highest-signal part of a skill; add to it whenever a run fails a new way. Done 2026-09-24. 43/43 skills: existing Environment, Failure modes, Known state, pitfalls, and lessons sections renamed; lesson bullets regrouped out of Rules; 11 skills with no recorded failure carry "None recorded yet". Rule in README Authoring rule 8, skillify template and compliance checklist; enforced by `tests/test_skill_structure.py`.

## Move shared environment gotchas out of individual skills

Depends on the agent-system TODO that adds these to `prompts/core.md` (so non-Claude harnesses keep them). Remove them here only after that lands.

- [x] `ls` aliased to a hanging git-aware tool / use `/bin/ls` — in: deep-interview, mail-digest, project-sync, publish-to-github, research-ingest, research-interview, spaced-recall. Done 2026-09-24. Agent-system `prompts/core.md` landed and installed (55baa26); removed from all seven, plus the pointer in morning-interview.
- [x] zsh aborts on a non-matching glob — in: deep-interview, mail-digest, morning-interview, research-ingest, research-interview, spaced-recall. Done 2026-09-24. Also removed from publish-to-github. The structure test fails if either gotcha reappears in a skill.

## Split the longest single-file skills

Move reference material into sibling files and point to it by situation from SKILL.md.

- [x] calendar-block (164 lines). Done 2026-09-24. Fit mode moved to `fit-mode.md`; SKILL.md 122 lines.
- [x] mail-digest (154 lines). Done 2026-09-24. Daily-note block to `note-block.md`, scheduling to `scheduling.md`; SKILL.md 118 lines.
- [x] collaborator-sweep (150 lines). Done 2026-09-24. Phase 2 interview moved to `interview.md`; SKILL.md 128 lines.
- [x] daily-note (142 lines). Done 2026-09-24. Time blocking moved to `time-blocking.md`; SKILL.md 113 lines.

## Optional

- [x] Have `plan-then-ship` and `adversarial-review` emit their plan or review as an HTML file (side-by-side approaches, severity-coloured findings) instead of Markdown. Done 2026-09-24. `render_plan.py` (approaches side by side, chosen marked) and `render_review.py` (severity-coloured findings), stdlib, tested in `tests/test_report_renderers.py`. The plan page and review rounds are HTML; `SPEC.md` stays Markdown because it is the implementer's contract and travels in prompts.
- [x] `research-ingest` handles material on disk only. Consider a web-sources path (list of URLs → one distilled note), or skillify it separately if it recurs. Done 2026-09-24. Added a `## Web sources` path (links → one distilled note) and updated its description; research-survey still owns topic research without links, and its description now says so.
