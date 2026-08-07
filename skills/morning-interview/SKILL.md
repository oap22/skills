---
name: morning-interview
description: Render today's daily note from Linear and Calendar, then interview Owen one question at a time about what's actually coming up today, writing his answers into the note as they come. Use when he says "morning interview", "what's on today", "interview me about my day", "morning check-in", "plan my day", or when the 6:30 morning routine fires.
---

# Morning Interview

The connectors know what's *scheduled*. They do not know what's coming. A ride to catch, a professor who might reply, a lab that's due but was never filed, the fact that he slept four hours — none of that is in Linear or Calendar, and all of it decides how the day actually goes.

This skill renders the machine-knowable half first, then asks about the rest.

**Vault:** `/Users/owenpacetti/Owen's Awesome Vault`
**Note path:** `School/Daily TODO/YYYY-MM-DD.md`
**Template:** `Templates/Daily Note.md`
**Linear:** workspace `owenp22` · team **Owen's Operations** (`OWE`) · projects School / Research / Personal
**Calendar:** `America/Chicago`

This absorbs the old `daily-note-render` routine — it does that render itself, then interviews. Read `.system/productivity-abstractions.md` for the tool boundary before changing how anything files.

## The two ways this starts

**Unattended (the 6:30 fire).** Owen is asleep. Do the render, write the brief, ask the *first* question in the note and in the run output, and stop. Do not fabricate answers, do not guess at a Top 3 and present it as agreed. A morning where nobody answers should still leave a fully rendered note.

**Attended (he invoked it, or replied to the fire).** Render if it hasn't happened yet, then run the interview live.

If the note already carries today's `interview-done` stamp, don't re-interview — say it's done and offer a refresh of the rendered block only.

## Steps

### 1. Resolve today

```bash
TZ=America/Chicago date +%Y-%m-%d
```

Never hardcode, never trust a date from earlier in the conversation. If `School/Daily TODO/<date>.md` exists you are refreshing — preserve everything outside the marked blocks. If not, create it from the template, substituting `{{date}}`, `{{yesterday}}`, `{{tomorrow}}`.

### 2. Render the day (Linear + Calendar)

This is the `daily-note` skill's job — invoke it if resolvable. Otherwise, inline:

- **Linear:** issues for team Owen's Operations, `assignee: "me"`, `state: "Todo"` plus In Progress, `fields: ["id","title","project","priority","status","dueDate","url"]`. Group School → Research → Personal; sort priority ascending, remembering **1 = Urgent, 4 = Low, 0 = None** — a naive sort puts "no priority" on top. Glyphs: 🔴 Urgent · 🟠 High · 🟡 Medium · ⚪ Low. One table per project, columns `P | Issue | link`, legend at the bottom. The whole thing goes between `<!-- linear:start -->` and `<!-- linear:end -->` and nothing outside those markers is touched.
- **Calendar:** today's events, `orderBy: startTime`, `timeZone: America/Chicago`. Fill `## Schedule` with `HH:MM – HH:MM`, summary, and `📆 [Calendar](htmlLink)`. Skip `WORKING_LOCATION` and `BIRTHDAY`. Events are not tasks.

Stamp `linear-synced: "<ISO timestamp>"` in frontmatter.

**If a connector fails, say which one, in the note.** Write `*Linear unreachable at 06:38 — this section is stale.*` inside the block. An empty section reads as "nothing to do today," which is a lie the whole routine exists to avoid.

### 3. Show the day back before asking anything

Open with the picture, not a question. Total scheduled hours, the largest free gap, count of urgent issues, anything due today. Two or three lines.

This is the same principle as `deep-interview`: **never ask what you can read.** "You've got 09:00–14:00 blocked and one 🔴 — is that the whole day?" is worth answering. "What's on today?" makes him recite his own calendar back at a machine that already has it.

### 4. Interview — one question per message

**Never batch.** A numbered list of six questions gets six shallow answers. One question gets a real one. Keep the framing around it to a line — a long preamble recreates the problem.

Let each answer choose the next question. Start with the biggest hole in the render.

Territory worth reaching, as threads and not a checklist:

- **Unscheduled fixed time** — rides, commutes, anything with a departure time that isn't an event
- **Today's real deadline** — the thing due that never became a Linear issue
- **Waiting on** — replies expected today, from whom, and what stalls without them
- **Capacity** — sleep, energy, anything physical that shrinks the day
- **The one thing** — if only one item lands, which one
- **Anything he already knows will go wrong**

Stop when the answers stop changing the plan. Six good questions beats fifteen dutiful ones; a morning routine that outlasts the coffee gets abandoned.

### 5. Write as you go, not at the end

After each answer, put it in the note. Long conversations get compressed and unwritten answers are lost answers.

Where each kind of answer files:

| Answer | Destination |
|---|---|
| Fixed time not on Calendar | a `## Schedule` row, Source `🗣 interview` (no Calendar link) |
| New actionable | `## Captured` as a checkbox — **not** Linear, not from a 6:30 routine |
| Waiting-on / context / capacity | the `<!-- interview:start -->` block |
| A real commitment to someone | `30-Brain/Commitments/` per the Brain rules |

The interview block lives under its own heading, below `## Schedule`:

```markdown
## Morning Check-in

<!-- interview:start -->
*Asked 06:38 · answered 07:12.*

**Capacity** — ~5h sleep, running on short rest.
**Unscheduled** — ride to campus leaves 08:20, not on Calendar.
**Waiting on** — Dr. Vance reply re: undergrad research (OWE-5); nothing else blocks on it.
**Expects to go wrong** — the 14:15 drive will eat the afternoon block.
<!-- interview:end -->
```

That block is regenerated wholesale on re-run. Everything outside it — Top 3, Captured, Notes — is his and is never overwritten.

If he never answered, the block says so and carries the parked question:

```markdown
<!-- interview:start -->
*Asked 06:38 — not yet answered.*

> Q: You've got 09:00–14:00 blocked and one 🔴. Is that the whole day, or is something else landing?
<!-- interview:end -->
```

### 6. Top 3, only after the interview

Propose three, weighted: Urgent > blocks other work > at-risk (unbacked repos, expiring tokens) > due today > stale-but-active. One line of reason each, plus a `🔗 [OWE-nn](url)` link.

**Fit them to what he just told you.** Three deep-work items on a day he described as five hours of meetings and four hours of sleep is a plan that fails by 10am — and now you have no excuse, because he said so.

Never overwrite a Top 3 he already wrote. Unattended runs propose it as a draft in the run output and leave the note's Top 3 alone unless it's empty.

### 7. Stamp and close

Set `interview-done: "<ISO timestamp>"` in frontmatter when he actually answered — that's what stops a re-run from re-interviewing. Leave it unset on an unattended fire.

Close by reading back the three things that changed versus the raw render. If nothing changed, say that too — it's evidence the render is good enough and the interview can get shorter.

## Rules

- **One question per message.** The rule the whole skill rests on.
- **Never ask what Linear, Calendar, or the vault already answers.** Present it for correction instead.
- **Only marked regions are regenerated.** `<!-- linear:* -->` and `<!-- interview:* -->`. Top 3, Captured, and Notes are his.
- **Never check off a rendered Linear issue in the vault.** State changes go to Linear.
- **A 6:30 routine does not write to Linear.** It captures; promotion is `vault-to-linear`'s job, with him present.
- **"Skip" ends a thread instantly.** Health, money, and sleep get asked plainly and dropped without friction.
- **Don't turn it into advice.** A line or two of implication is right; a plan is a different task.
- **Verify proper nouns against written sources.** He dictates; names arrive garbled. A repo namespace, author list, or email beats a spoken name — confirm rather than silently correcting.
- **Resolve the date at runtime**, `America/Chicago`.
- **Never delete vault content** to reconcile with anything. Ask first, always.

## Scheduling this

**Local** scheduled task — never a cloud routine. A cloud agent cannot reach the vault, Linear, or Calendar and fails silently every morning. See the `local-routine` skill.

Live routine: `morning-interview`, `30 6 * * *` America/Chicago. It replaces `daily-note-render`, which is disabled — **do not re-enable it**, or the note gets rendered twice each morning by two tasks racing on the same file.

Two things that surprise people, both true here:

- It only runs while the Claude app is open. Closed at 6:30 → runs at next launch, so a note may be stamped hours after the date in its filename.
- The reported time is later than the cron (`06:38` for `30 6 * * *`). That's deterministic jitter, not a bug.

## Environment

- zsh aborts on non-matching globs — `for f in dir/*.md` dies if the directory is empty. Use `find | while read`.
- `ls` is aliased to a git-aware tool that hangs in large or fresh repos. Use `/bin/ls`.

## Untested

- **A live 6:30 fire.** The routine is created and the render half is inherited from a verified `daily-note`, but no morning has actually run interview-and-answer end to end yet. Expect the first real fire to pause on connector permission prompts.
- **Re-run guarding.** `interview-done` short-circuiting a second same-day run is written but unexercised.
- **The parked-question path** — asked at 6:30, answered at noon in a different session — is the most likely thing to be wrong.
