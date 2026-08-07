---
name: daily-note
description: Build or refresh today's daily note in the Obsidian vault, rendering open Linear issues and Google Calendar events into it. Use when the user says "daily note", "plan my day", "what's on today", "today's tasks", "morning review", or "refresh my daily note".
---

# Daily Note

Today's note is a **rendered view**, not a task list. Linear owns issue state, Calendar owns fixed time, the vault owns context and whatever gets captured during the day.

**Vault:** `/Users/owenpacetti/Owen's Awesome Vault`
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

### 5. Stamp and write

Set `linear-synced: "<ISO timestamp>"` in frontmatter so a later refresh can tell how stale the render is.

### 6. Handle Captured

The `## Captured` section is the one place vault checkboxes still belong — things that came up today and aren't in Linear yet.

On refresh, **read it**. If it has items, offer to promote them into Linear (that's the `vault-to-linear` skill's job). Promote, then remove them from Captured — leaving them behind recreates the duplicate-state problem the whole design exists to avoid.

## Rules

- **Only the marked region is regenerated.** Never clobber Top 3, Schedule notes, Captured, or Notes.
- **Never check off a rendered issue in the vault.** State changes go to Linear. The rendered tables have no checkboxes on purpose — if a checkbox appears there, something regressed.
- **Priority 0 means "None", not "highest".** Sort accordingly.
- **Resolve the date at runtime.** Never hardcode, and don't trust a stale date from earlier in the conversation.
- **Don't create tomorrow's note ahead of time** unless asked — empty future notes clutter the folder and break the "is it rendered?" signal.
- **Never delete vault content** to reconcile with Linear. Ask first, always.

## Untested

- **Refresh-in-place.** Built and verified on a first render (`2026-08-06`); replacing an existing marked block while preserving surrounding content has not yet been exercised against a note the user has edited by hand.
- **In Progress issues.** The team has the status but no issue has used it yet, so its placement in the rendered tables is unverified.
