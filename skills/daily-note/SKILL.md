---
name: daily-note
description: Build or refresh today's daily note in the Obsidian vault, rendering open Linear issues and Google Calendar events into it. Use when the user says "daily note", "plan my day", "what's on today", "today's tasks", "morning review", or "refresh my daily note".
---

# Daily Note

Today's note is a **rendered view**, not a task list. Linear owns issue state, Calendar owns fixed time, the vault owns context and whatever gets captured during the day.

**Vault:** `$HOME/Owen's Awesome Vault`
**Note path:** `School/Daily TODO/YYYY-MM-DD.md`
**Template:** `Templates/Daily Note.md`
**Linear:** workspace `owenp22` · team **Owen's Operations** (`OWE`) · projects School / Research / Personal

Read `.system/productivity-abstractions.md` for the tool boundary before changing how any of this files.

## The rendered region

Everything between these markers is **generated and disposable**:

```markdown
<!-- linear:start -->
...
<!-- linear:end -->
```

Refreshing replaces that whole block and nothing else. Content outside the markers — Top 3, Schedule, Captured, Notes — is the user's and is never overwritten.

## Steps

### 1. Resolve today

Get the real local date; don't assume. The vault is `America/Chicago`.

```bash
date +%Y-%m-%d
```

If `School/Daily TODO/<date>.md` exists, you are **refreshing** — preserve everything outside the markers. If not, create it from the template, substituting `{{date}}`, `{{yesterday}}`, `{{tomorrow}}`. Links to nonexistent neighbor notes are fine.

### 2. Pull Linear

List issues for team Owen's Operations, `assignee: "me"`, `state: "Todo"`, plus anything In Progress. Request `fields: ["id","title","project","priority","status","dueDate","url"]`.

Group by project (School → Research → Personal), and within each sort by priority ascending — Linear uses **1 = Urgent, 4 = Low, 0 = None**, so a naive numeric sort puts "no priority" first. Map to glyphs:

| Value | Glyph |
|---|---|
| 1 Urgent | 🔴 |
| 2 High | 🟠 |
| 3 Medium | 🟡 |
| 4 Low | ⚪ |

Render one table per project with columns `P | Issue | link`. Keep the legend line at the bottom of the block.

### 3. Pull Calendar

List events for today, `orderBy: startTime`, `timeZone: America/Chicago`. Fill the `## Schedule` table with `HH:MM – HH:MM`, the event summary, and `📆 [Calendar](htmlLink)`.

Do **not** turn events into tasks. If an event clearly needs prep, that prep is a Linear issue, not a schedule row.

Skip `WORKING_LOCATION` and `BIRTHDAY` event types — they are noise in a day plan.

### 4. Propose a Top 3

Only if the section is empty — never overwrite a Top 3 the user already wrote.

Pick exactly three, weighting: Urgent > blocks other work > at-risk (unbacked repos, expiring tokens) > due today > stale-but-active project. Give each a one-line reason and a `🔗 [OWE-nn](url)` link. Prefer items that actually fit the gaps in the Schedule table — three deep-work items on a day with seven hours of meetings is a plan that fails by 10am.

### 5. Block time for the Top 3

Write each Top 3 item into Google Calendar as a focus block, fitted around what's already there. This is the one step that **writes to a system outside the vault** — treat it conservatively.

**Find the gaps.** Working window is **08:00–20:00** America/Chicago. Take the events from step 3, ignore all-day events (they don't consume hours) but *do* respect `OUT_OF_OFFICE`. Leave a **15-minute buffer** on each side of an existing event. What's left are the candidate gaps.

**Size each item first.** A block should be as long as the work, not a fixed slab. If the Linear issue has an `estimate` set, that wins — map points to time as 1 → 30m, 2 → 1h, 3 → 2h, 5 → 3h, 8+ → treat as open-ended (below). As of 2026-08-06 no issue has an estimate, so in practice you are inferring from the shape of the task:

| Size | Looks like | Examples |
|---|---|---|
| **30 min** | one bounded action, obvious done state | send an email, reissue a token, add an SSH key, add a git remote, check a page for a decision |
| **60 min** | bounded but multi-step, or writing something short | a literature note, bringing an index current, inbox triage |
| **90 min** | real focus, edges not fully known | benchmark two models, build out a workflow, drill a topic |
| **open-ended** | cannot finish in a day | train a model, reverse-engineer a repo end to end, pick *and start* a Kaggle competition |

**Open-ended items get one 90-minute block to *start*, not an attempt to schedule the whole thing** — title it `🎯 OWE-nn — start: <title>` so the block promises what it can deliver. A block that silently implies "finish this today" is a plan that fails at 10am and teaches Owen to ignore the calendar.

**Then fit them.** Walk the Top 3 in order — item 1 takes the earliest viable gap, so the most important thing lands before the day erodes. A block goes in only if a gap fits its full size; if the only gap is smaller, shrink by at most 30 minutes, and below that skip it rather than cram. Never overlap an existing event, never run past 20:00, and leave **15 minutes between consecutive blocks** — otherwise an empty day becomes one unbroken slab.

**Cap the day at 4 hours of blocks total.** Three genuinely large items is a signal that the Top 3 was overambitious, not a reason to fill the calendar.

Put the estimate in the Top 3 line in the note (`— ~30m`) so the reasoning is visible and Owen can correct it. If he keeps correcting the same issue, that's the cue to set a real `estimate` in Linear and let it win.

**Create with an idempotency marker.** The summary is `🎯 OWE-nn — <short title>`. That `🎯 OWE-nn` prefix is the marker the next run keys on.

```
summary:     🎯 OWE-5 — Email Dr. Vance about medical AI
startTime / endTime / timeZone: America/Chicago
description: <one-line reason from the Top 3> + the Linear URL
eventType:   DEFAULT
availability: AVAILABILITY_BUSY
colorId:     <the Linear project's color — see below>
```

**Color the block by its Linear project**, so a focus block is visually the same category as the fixed time around it:

| Linear project | `colorId` |
|---|---|
| School | `9` Blueberry |
| Research | `6` Tangerine |
| Personal | `8` Graphite |

The full scheme lives in `.system/calendar-conventions.md` and in the `calendar-block` skill. Never leave `colorId` unset — Google's default renders as Blueberry and would silently mislabel every Research and Personal block as School.

Use `DEFAULT`, not `FOCUS_TIME` — focus-time events can auto-decline real invitations, which is a side effect nobody asked for.

**Before creating anything, re-list today's events and skip any `OWE-nn` that already has a `🎯 OWE-nn` block.** The routine has jitter and gets run by hand too; without this check a double-run doubles the calendar.

If nothing fits, create nothing and say so in the summary. A day with no room is a real answer.

### 6. Stamp and write

Set `linear-synced: "<ISO timestamp>"` in frontmatter so a later refresh can tell how stale the render is.

### 7. Handle Captured

The `## Captured` section is the one place vault checkboxes still belong — things that came up today and aren't in Linear yet.

On refresh, **read it**. If it has items, offer to promote them into Linear (that's the `vault-to-linear` skill's job). Promote, then remove them from Captured — leaving them behind recreates the duplicate-state problem the whole design exists to avoid.

### 8. Push the day

Send one `PushNotification` with the Top 3 and how many blocks landed. Under 200 characters, one line, no markdown — mobile truncates and this is the only thing that reaches Owen before he opens the vault.

```
Top 3: Email Dr. Vance (OWE-5) · SSH key→GitLab (OWE-9) · git remote for Design System (OWE-21) — 2 blocks on your calendar.
```

Abbreviate titles hard; the OWE id carries the precision. If nothing could be scheduled, say that instead of padding — `no room today, calendar is full` is the useful message.

This reaches the phone only when Remote Control is connected; otherwise it's a desktop notification. Either way, send it — the routine runs at 06:38 when Owen is away from the terminal, which is exactly the case notifications are for.

## Rules

- **Only the marked region is regenerated.** Never clobber Top 3, Schedule notes, Captured, or Notes.
- **Never check off a rendered issue in the vault.** State changes go to Linear. The rendered tables have no checkboxes on purpose — if a checkbox appears there, something regressed.
- **Priority 0 means "None", not "highest".** Sort accordingly.
- **Resolve the date at runtime.** Never hardcode, and don't trust a stale date from earlier in the conversation.
- **Don't create tomorrow's note ahead of time** unless asked — empty future notes clutter the folder and break the "is it rendered?" signal.
- **Never delete vault content** to reconcile with Linear. Ask first, always.
- **Never delete, move, or edit a calendar event you didn't create.** Time-blocking only ever *adds*, and only into free gaps. If a `🎯` block is now wrong, leave it — say so in the summary and let Owen clear it.
- **Only block today.** Never write focus blocks onto a future date, for the same reason the note isn't built ahead.

## Scheduling this

Use a **local** scheduled task, never a cloud routine — see the `local-routine` skill. A cloud agent cannot reach the vault or the Linear/Calendar connectors, and fails silently every morning.

The live routine is **`morning-interview`**, `30 6 * * *` America/Chicago — it performs this render and then interviews Owen about what the connectors can't see. The old render-only `daily-note-render` task is **disabled**; don't re-enable it, or two tasks race on the same file every morning.

This skill is still the right thing to invoke for an on-demand render with no interview.

## Untested

- **In Progress issues.** The team has the status but no issue has used it yet, so its placement in the rendered tables is unverified.
- **A day with a partially-filled Schedule table.** Verified against a full calendar day and an empty one; the merge behavior when the user has hand-added a row is unexercised.
- **Time-blocking (step 5) has never run.** Added 2026-08-06, first live exercise is the 2026-08-07 06:38 render. The gap math, the 15-minute buffers, and the `🎯 OWE-nn` duplicate check are all unverified against a real calendar.
- **Duration estimates are guesses, and nothing checks them.** The size rubric has never been compared against how long anything actually took. The feedback loop is Owen noticing a block was wrong — there is no automatic correction. If estimates prove consistently off, the fix is real `estimate` values in Linear, not a more elaborate rubric.
- **The push notification (step 8) has never fired from the scheduled run.** Whether it reaches the phone depends on Remote Control being connected at 06:38.

*(Refresh-in-place was verified 2026-08-06: replacing the marked block preserved Top 3, Schedule, Captured, and Notes intact.)*
