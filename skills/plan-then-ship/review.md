# Adversarial review

Run this **before commit, push, or PR**. The feature branch already exists from `SKILL.md` §4 / `ship.md`. Do not commit from the review pass. The reviewer is the planner/reviewer role in `models.md`, not the implementer.

Attack the change. The job is to find reasons not to ship, then only ship if those reasons fail. The lensed attack is `adversarial-review`; this file adds spec fidelity, scoring, and the repair loop.

## Pass 0 — evidence

Run the relevant commands in the spec's Tests section and retain their output. Summarize outcomes and any unavailable checks; do not claim unrun tests passed. Documentation-only changes can use inspection rather than invented execution tests.

Redact secrets in the paste — tokens, passwords, API keys, `Authorization` headers, private keys, and URLs that embed credentials — replace the value with `REDACTED`. Never paste raw secrets. Concise outcome summaries are sufficient when full logs add no value.

"Should pass," "looks fine," "the implementer said tests were green" — all fails. Re-run it yourself. If the implementer ran in the cloud, re-run the tests **here** on the fetched branch. Their log is not your evidence.

If tests are red, that is already a critical. Repair starts; do not skip the rest of the review, because the other findings are what the next implementer pass must also fix.

## What to attack

Score every finding **critical** (blocks ship, starts a repair loop) or **suggestion** (does not block, does not loop).

**Spec fidelity (this file owns it).**
1. Diff the working tree against `.plan-then-ship/SPEC.md`. Files not in Touch (except listed tests, and `.gitignore` if it only gained a `.plan-then-ship/` ignore) are critical. Missing edits from Per-file edits are critical. "Improvements" the spec did not ask for are critical — revert them. `.gitignore` is planner work; see `ship.md`. Do not fail the implementer for it.
2. Any edit in the Do-not-touch list is critical.
3. Walk the spec's acceptance-criteria checklist. Any item that is not observably true is critical.

**Everything else delegates to `adversarial-review`.** Run its steps 1–5 on the same diff: scope, pick 2–4 lenses from its `lenses.md` (always include Spec conformance & completeness, plus Test honesty when existing tests changed), fan out, collect findings with a concrete failure scenario each, and run its verifier after the repair. Without parallel subagents, run the lenses sequentially yourself as that skill describes. Every finding it returns is scored here: production bugs, silent failures, and uncovered acceptance criteria are critical; style and naming are suggestions. Its fix step is not used — repairs go through the Repair prompt below so the implementer stays the single owner.

Cursor: if `bugbot` or `security-review` agents exist, launch them here as well. Their criticals join this list. Their output does not replace Pass 0.

## Output

```markdown
# Review — round N

## Tests
command:
<paste>
result: green | red

## Critical
- [file:line] claim. Why it violates the spec or will fail in production.

## Suggestions
- [file:line] claim. Not a blocker.

## Spec fidelity
touched extra: none | <paths>
missing spec edits: none | <list>
freelance "improvements": none | <list>

## Progress (round 2+)
criticals last round: N
criticals this round: N
closed: <ids or one-liners>
survived unchanged: <ids>
reintroduced: <ids>
stuck rule fired: none | no-progress | same-finding | oscillation | spec-is-wrong
```

Round 1 has no Progress block. Rounds 2+ must fill it — that is how the loop knows whether to continue.

## Stuck rules

Evaluated after each review that still has criticals or red tests. First match routes to the bounded escalation rules in `SKILL.md`. A contradictory spec needs a user decision; do not try to implement around it. Do not ship unresolved critical defects.

| Rule | When it fires |
|---|---|
| **No progress** | The same root cause remains unresolved with no new evidence or working correction. |
| **Same finding, unchanged** | A critical at the same location with the same claim survived a repair. |
| **Oscillation** | This round reintroduces a critical that the previous round had closed. |
| **Spec is the problem** | The implementer or reviewer can show the spec is contradictory, incomplete, or wrong. Escalate to Owen; do not spend another implementer pass. |
| **Loop cap** | Review pass 5 (initial + 4 repairs) still has criticals or red tests. Do not start a fifth repair. Backstop, not the expected length. |

Suggestions never enter these counts. Promoting a suggestion to critical so the loop can "keep improving" is a miss — that is how it fails to converge.

## Repair prompt

When not stuck, send the implementer the critical list, the **full spec text**, the same feature-branch name, and:

> Repair only the critical findings below. Do not address suggestions. Do not expand scope. Stay on feature branch `<branch>`. Re-run the spec's test commands and paste the output with secrets redacted. Spec text is included in this prompt; `.plan-then-ship/SPEC.md` is the same-tree copy.

Then re-run this whole file from Pass 0. Do not review from memory of the last diff. After a cloud/isolated repair, fetch the branch again.
