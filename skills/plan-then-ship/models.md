# Model mapping

Roles are defined in `SKILL.md`. This file is only the names, and it will go stale. If a spawn fails because the model id is unknown, stop and tell Owen rather than silently inheriting the parent.

Use the **planner** for planning and for review. Use the **implementer** for writing code. Never invert that.

| Harness | Planner / reviewer | Implementer |
|---|---|---|
| Claude | Opus 5 (current parent if it is already Opus) | Sonnet |
| Codex | Sol | Luna |
| Cursor | Current parent, unless it is on the implementer deny-list below; otherwise Sol (`gpt-5.6-sol-medium`) | Composer (`composer-2.5`). Grok (`cursor-grok-4.6-low`) if Owen named Grok. |

Do not use a fuzzy "strong model" test. The implementer **deny-list** is the only classifier:

- Sonnet (any `sonnet` / `claude-sonnet` id)
- Luna (`gpt-5.6-luna-medium`, or the session calling itself Luna)
- Composer (`composer-2.5`, `composer-2.5-fast`)
- Grok (`cursor-grok-4.6-low`, or the session calling itself Grok)

If the current session matches any of those names or ids, you are the implementer. Refuse to write a spec. Every other named model is the planner. If you cannot tell which model you are, ask once and wait. Do not guess.

## Spawn vs degrade

Always include the **full spec text** in the implementer prompt, plus the path, the feature-branch name, and the `origin` URL. Path-only prompts fail the moment the agent is not this working tree.

**Same-tree spawn** (same cwd, same uncommitted files): preferred when the harness offers it. Spawn the implementer with the id in the table. Wait. Do not also write the code in the parent.

**Cloud or isolated spawn** (separate VM, worktree, or clone): first-class, not a consolation prize. Same prompt, plus: branch from the repo default branch onto the feature-branch name from `ship.md`; commit only Touch/Tests; push that branch to `origin`; do not merge. When it returns, fetch that branch here (`ship.md` § After a cloud or isolated implementer) and review *that* tree.

**If the harness cannot spawn a named-model agent at all**, do not fake a handoff. Stop after the spec is approved and give Owen:

1. The implementer name from the table.
2. The spec text.
3. This sentence to send after switching:

> Implement this spec exactly. Do not expand scope. Do not improve the design. Do not touch files the spec marks do-not-touch. Work on the feature branch named in the spec's ship notes, never main/master. Run the test commands in the spec and report the actual output, redacting secrets. If the spec is contradictory or incomplete, stop and say so — do not invent a design.

Review after that session returns, still as the planner/reviewer model. If that session was also isolated, fetch its branch before reviewing.

## Cursor-specific

Plan mode may be the planning step. Still write `.plan-then-ship/SPEC.md` before asking for approval — a Plan-mode bubble is not a file the implementer can open.

When review agents named `bugbot` or `security-review` exist, launch them during the review step *in addition* to `review.md`. They do not replace running the spec's test commands.
