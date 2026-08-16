---
name: vault-to-linear
description: Sweep the Obsidian vault for open tasks and promote them into Linear issues under the right project, without creating duplicates. Use when the user says "populate Linear from my vault", "sync my tasks to Linear", "pull my open tasks into Linear", or after a weekly review when vault checkboxes have piled up.
---

# Vault → Linear

Turn the vault's scattered `- [ ]` checkboxes into a real, prioritized Linear backlog. Run it on first setup and again whenever vault tasks have accumulated.

**Vault:** `/Users/owenpacetti/Owen's Awesome Vault`
**Target:** workspace `owenp22` · team **Owen's Operations** (`OWE`) · projects **School**, **Research**, **Personal**

Read `.system/productivity-abstractions.md` first — it defines the tool boundary and is the thing to update if the boundary changes. Linear owns task *state*; the vault owns *context*. Never mirror state into both.

## Steps

### 1. Confirm the target before writing

Linear "get user" with `me`, then list projects on the team. Confirm the three projects exist and the workspace slug in their URLs matches. If a project is missing, run `linear-project-setup` first.

### 2. Read what's already in Linear

List existing issues on the team **before** sweeping. This is the dedupe set — match on normalized title: lowercase, punctuation stripped, whitespace collapsed. One fixed rule, applied the same way to both sides — an improvised looser match double-files on the next run. Re-running this skill must not double-file tasks that were promoted last time.

### 3. Sweep the vault

Grep for open checkboxes, excluding the noise:

```bash
grep -rn --include="*.md" -- "- \[ \]" . \
  | grep -vE "^\./(Templates|\.system|claude-outputs|\.claude)/" \
  | grep -v "README.md"
```

Then read these sources directly, since the best tasks are not always checkboxes:

| Source | What to take |
|---|---|
| `02-Projects/*.md` | § Next Actions and unchecked § Status items — **`status: active` only** |
| `03-Areas/*.md` | Recurring rituals (daily/weekly) |
| `01-Maps/MOC - *.md` | Open **experiments**, not open questions |
| `30-Brain/Commitments/*.md` | Frontmatter `status` — skip anything `done` |
| Conversation / meeting notes | Explicit action lists, often the highest-value items |

Check project frontmatter `status` before taking anything. Paused and done projects have stale next-actions that look live.

### 4. Filter hard

Most checkboxes in a vault are not tasks. Drop:

- **Open questions** in MOCs ("Which chunk size for literature notes?") — research prompts, not actions
- **Template placeholders** — empty `- [ ]` in `Templates/`
- **Setup checklists** under `.system/` — one-time install steps, usually already done
- **Archived skill bodies** — `.system/skills-archive/` is full of `- [ ]` that are documentation examples
- Anything on a **paused or done** project

A good issue has a clear done state and a plausible day it gets worked on. If you can't picture finishing it, it's context, not a task.

### 5. Classify and prioritize

Route by the project note's `type` frontmatter (`school` / `research` / `personal`) where it exists; otherwise by content. Coursework and clubs → School. Papers, experiments, reading → Research. Tooling, side projects, life admin → Personal.

Priority signals worth honoring — these come from the vault's own language, not your guess:

| Signal in the note | Priority |
|---|---|
| "single most repeated piece of advice", named blocker | 1 Urgent |
| Blocks other work; unbacked/at-risk work (no git remote) | 2 High |
| Ordinary next action, recurring ritual | 3 Medium |
| Someday, exploratory, "decide whether to" | 4 Low |

### 6. Create the issues

One `save_issue` per task. Set `team`, `project`, `assignee: "me"`, `state: "Todo"`, and `priority`.

- **`state` defaults to Backlog if you omit it.** Pass `"Todo"` explicitly or the whole import lands invisible.
- Put the **vault source path** in every description — `Source: 02-Projects/Foo.md § Next Actions`. This is what makes the issue traceable back to its context, and it's the first thing missing when a backlog stops being trustworthy.
- Attach real URLs via `links` (OpenReview, repos) — they render as attachments.
- For recurring rituals, say so in the description: *"Recurring — repeat weekly rather than closing permanently."* Linear has no recurrence in this API.
- **Never copy a secret** into an issue. Tokens, PATs, keys: reference that one needs reissuing, never the value.

### 7. Close the loop in the vault

The sweep is only half the job. Also:

- Add `linear: <project-url>` to the frontmatter of each project note that produced issues.
- Record the run in `30-Brain/Sources/sync-state.md`: date, highest issue id as cursor, count, and — importantly — **what you deliberately skipped and why**. Future runs read this to stay consistent.
- Leave the original `- [ ]` boxes in place as context. Do not delete vault content to "finish" a sync.

### 8. Report

Group by project, show priority, and state plainly what was skipped. A sync that silently dropped half the vault reads as complete when it isn't.

## Rules

- **Dedupe against Linear before creating**, never after. There is no cheap bulk delete.
- **Only `status: active` projects.** This is the single biggest source of junk issues.
- **Open questions are not tasks.** MOC question lists stay in the vault.
- **`state: "Todo"` must be explicit** — the default is Backlog.
- **Every issue cites its vault source.** No orphan issues.
- **Never write secrets** into an issue description.
- **Never delete vault notes or checkboxes** — the vault rule is ask-first, always.
- If the vault's doctrine file contradicts what the user is asking for, **say so and update the doctrine** rather than leaving both versions live.

## Untested

- **Re-run dedupe.** This procedure was built on a first population into an empty backlog; the title-matching dedupe path in step 2 has not been exercised against existing issues.
- **Linear → vault direction.** Nothing here writes completed Linear state back into the vault. If issues get closed in Linear, vault checkboxes go stale silently.
