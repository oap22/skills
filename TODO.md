# TODO

Open changes from the 2026-09-24 review of skills against the claude.dev skills post ("Lessons from building Claude Code: How we use skills"; summary in vault note "Using Claude Well").

## Gotchas sections

- [ ] **Give every skill a `## Gotchas` heading.** None has one today. Many already have `## Environment` or `## Rules` sections doing the same job; rename or regroup those rather than writing new content. The post calls Gotchas the highest-signal part of a skill; add to it whenever a run fails a new way.

## Move shared environment gotchas out of individual skills

Depends on the agent-system TODO that adds these to `prompts/core.md` (so non-Claude harnesses keep them). Remove them here only after that lands.

- [ ] `ls` aliased to a hanging git-aware tool / use `/bin/ls` — in: deep-interview, mail-digest, project-sync, publish-to-github, research-ingest, research-interview, spaced-recall
- [ ] zsh aborts on a non-matching glob — in: deep-interview, mail-digest, morning-interview, research-ingest, research-interview, spaced-recall

## Split the longest single-file skills

Move reference material into sibling files and point to it by situation from SKILL.md.

- [ ] calendar-block (164 lines)
- [ ] mail-digest (154 lines)
- [ ] collaborator-sweep (150 lines)
- [ ] daily-note (142 lines)

## Optional

- [ ] Have `plan-then-ship` and `adversarial-review` emit their plan or review as an HTML file (side-by-side approaches, severity-coloured findings) instead of Markdown.
- [ ] `research-ingest` handles material on disk only. Consider a web-sources path (list of URLs → one distilled note), or skillify it separately if it recurs.
