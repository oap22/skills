---
name: local-routine
description: Schedule a recurring agent task that needs the local machine — the Obsidian vault, local files, or MCP connectors like Linear, Gmail, and Google Calendar. Use when the user says "run this every morning", "do this daily", "set up a routine", or "schedule this" AND the work touches local files or connected apps. For work that lives entirely in a GitHub repo, use the built-in /schedule (cloud) instead.
---

# Local Routine

There are two schedulers on this machine and they are not interchangeable. Picking wrong produces a routine that looks healthy in the UI and silently does nothing every single day.

## Pick the scheduler first

| | **Local** — `mcp__scheduled-tasks__*` | **Cloud** — built-in `/schedule`, `RemoteTrigger` |
|---|---|---|
| Runs on | This Mac, inside the Claude app | Anthropic cloud sandbox |
| Sees local files | **Yes** | No |
| Sees the Obsidian vault | **Yes** | No — the vault is not a git repo |
| MCP connectors | Whatever this app has connected | Only claude.ai connectors, often **none** |
| Needs a git repo | No | Effectively yes |
| Min interval | Cron, 1/min granularity | 1 hour |
| Timezone | **Local** (America/Chicago) | **UTC** — must convert |

**Default to local** for anything in Owen's world. The vault, Linear, Gmail, and Calendar all hang off this app. Cloud is only right for work that lives entirely inside a GitHub repo and needs no local state.

Verify before choosing rather than assuming: if `/schedule`'s setup notes say *"No MCP connectors found"* or *"Not in a git repo"*, that is the cloud path telling you it cannot do the job.

## Steps

### 1. Confirm it needs local

Ask what the task touches. Vault paths, `~/Developer`, Linear, Calendar, Gmail, Slack → local. A repo-only chore (dependency bumps, CI triage) → cloud, and hand off to `/schedule`.

### 2. Write a self-contained prompt

**Each run starts with zero memory of the conversation that created it.** The prompt is the entire context. Include:

- Absolute paths — vault root, target files, templates
- Which connectors to use and which workspace/team/account within them
- The exact output format expected
- Every preference the user expressed while setting it up
- What to do on partial failure — *"if Linear is unreachable, write what you have and say plainly which source failed"*. Without this, a failed connector renders as an empty section that reads like a fact.

Prefer telling it to invoke an existing skill by name, then inline the essential steps as fallback in case the skill isn't resolvable from that run's working directory.

### 3. Create it

```
mcp__scheduled-tasks__create_scheduled_task
  taskId: kebab-case
  cronExpression: "30 6 * * *"    # LOCAL time — do not convert to UTC
  description: one line for the sidebar
  prompt: the self-contained prompt
  notifyOnCompletion: true
```

Use `fireAt` (ISO 8601 with offset) instead for a genuine one-shot. Never fake a one-shot with cron.

### 4. Verify, and expect jitter

List the task afterwards. The reported time will be **later than the cron** — the scheduler adds a deterministic `jitterSeconds` (several minutes) to spread load. `30 6 * * *` showing as "06:38" is correct, not a bug. Check `cronExpression`, not the human-readable string, and tell the user so the drift doesn't look like an error.

### 5. Tell the user the two real limits

Both of these surprise people, and both are worth saying out loud:

- **It only runs while the Claude app is open.** If the app is closed at 6:30, it runs at next launch — so a note may be stamped hours after the date in its filename.
- **The first run will pause on permission prompts** for each connector it touches. Approvals are stored on the task and reused afterward.

### 6. Pre-approving: there is no "run now" tool

`mcp__scheduled-tasks__*` exposes only create, update, delete, list. **There is no run action.** (`RemoteTrigger`'s `run` is for cloud routines and will not touch a local task.)

The user clicks **Run now** in the Scheduled sidebar. Don't treat this as a limitation to work around — the approval prompts need the user present anyway, so the click and the approving are the same act. Triggering it behind their back would just stall on a prompt nobody answers.

Do **not** fake it by swapping `cronExpression` for a near-future `fireAt`: `fireAt` clears the cron, and the task auto-disables after firing. If the session ends before you restore the schedule, the user's routine is silently dead and they won't notice for days.

### 7. Record it

Note the routine in the doctrine file it serves (for vault work, `.system/productivity-abstractions.md`): task id, cron, that it's local and why, and the app-must-be-open caveat.

## Rules

- **Local unless proven otherwise.** Cloud cannot see the vault.
- **Cron is local time here** and UTC in the cloud scheduler. Mixing these up is a silent 5–6 hour offset.
- **The prompt must stand alone.** No "as we discussed", no relative dates — have it resolve the date at runtime with `TZ=America/Chicago date +%Y-%m-%d`.
- **Always instruct partial-failure reporting.** A silent empty section is worse than an error.
- **Never put secrets in a task prompt.** It's a plaintext file at `~/.claude/scheduled-tasks/<id>/SKILL.md`.
- **Deleting is destructive** — prefer `enabled: false` to pause, and ask before deleting either way.

## Untested

- **Behavior when the app is closed through several scheduled fires.** Documented as "runs on next launch"; whether it coalesces missed runs into one or replays them has not been observed.
