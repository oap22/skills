---
name: morning-interview
description: "Render the daily note, then interview Owen one question at a time about capacity, unscheduled commitments, and priorities. Use for \"morning interview\", \"morning check-in\", or a scheduled morning interview. Use day-check for a quick read-only day summary."
---

# Morning Interview

Before saving a daily note, use the vault's documented helper for every create or marker update. Its `note_lock` takes `.system/locks/daily-note.lock`; its update path re-reads the expected bytes under the lock and uses an atomic replace. Re-read the note and merge only this workflow's owned region. If the helper, lock, expected-bytes check, or atomic replace is unavailable, do not improvise a whole-file fallback: preserve the note and report the blocker. If markers are duplicated or unbalanced, preserve the file and report the structural problem. Scheduling statements below are historical setup notes: inspect the live task before reporting its status or changing it.

The connectors know what's *scheduled*. They do not know what's coming. A ride to catch, a professor who might reply, a lab that's due but was never filed, the fact that he slept four hours — none of that is in Linear or Calendar, and all of it decides how the day actually goes.

This skill renders the machine-knowable half first, then asks about the rest.

**Vault:** `/Users/owenpacetti/Owen's Awesome Vault`
**Note path:** `School/Daily TODO/YYYY-MM-DD.md`
**Template:** `Templates/Daily Note.md`
**Linear:** two workspaces, both rendered — `owenp22` / team **Owen's Operations** (`OWE`) on the default server, and `research-group-2627` / team **Research Group 26/27** (`RES`) on the `linear-research` server. Separate servers; querying only the first is how RES work stayed invisible for the render's first ten days.
**Calendar:** `America/Chicago`

This absorbs the old `daily-note-render` routine — it does that render itself, then interviews. Read `.system/productivity-abstractions.md` for the tool boundary before changing how anything files.

Before creating or refreshing a note, read `.system/note-creation.md` and the
Daily Note section of `.system/frontmatter-schema.md`. Use
`python3 .system/scripts/daily-note.py --vault . --date <date> --ensure` from
the vault root for creation and `--region interview --body-file` for this
skill's generated interview block.
Re-read immediately before each write and preserve the user's Chosen outcome,
any legacy Top 3, Schedule, Captured, Notes, and the `mail`/`linear` regions
owned by the other skills. The daily-note skill owns Linear rendering and its
`linear-rendered-at`/coverage/success fields; this skill must not advance those
fields from an interview-only write. Read connector status and retain truthful
partial or unavailable coverage in the report.

## The two ways this starts

**Unattended (the 6:30 fire).** Owen is asleep. Do the render, write the brief, ask the *first* question in the note and in the run output, and stop. Do not fabricate answers, do not guess at a Chosen outcome and present it as agreed. A morning where nobody answers should still leave a fully rendered note.

**Attended (he invoked it, or replied to the fire).** Render if it hasn't happened yet, then run the interview live.

If the note already carries today's `interview-done` stamp, don't re-interview — say it's done and offer a refresh of the rendered block only.

## Steps

### 1. Resolve today

```bash
TZ=America/Chicago date +%Y-%m-%d
```

Never hardcode, never trust a date from earlier in the conversation. If `School/Daily TODO/<date>.md` exists you are refreshing — preserve everything outside the marked blocks. If not, create it with `python3 .system/scripts/daily-note.py --vault . --date <date> --ensure` from the vault root and the documented template contract.

### 2. Render the day (Linear + Calendar; read the existing mail block)

Read `../daily-note/SKILL.md` and perform its **render-only** steps. Do not run its optional time-blocking step, promote captures, or fill Chosen outcome before the interview. Reuse its workspace verification, pagination, partial-failure, coverage, and Schedule-preservation rules. If the skill is unavailable, report the missing dependency and present the available day context in chat; do not reconstruct a second rendering contract.

### 3. Show the day back before asking anything

Open with the picture, not a question. Read the existing `## Mail` block after the render, without rerunning the mail sweep. Include any mail item marked delivery change, waiting-on-you, or must-know alongside total scheduled hours, the largest free gap, count of urgent issues, and anything due today. Say when the mail block is absent, stale, or reports an unavailable connector. Keep the overview to two or three lines.

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

If a piece of fixed time he mentions is genuinely load-bearing — a game, a ride, a window he can't be scheduled into — **offer to put it on Calendar** rather than only writing a Schedule row. A row in the note doesn't stop the next render from blocking over it. Use the `calendar-block` skill so it gets the right category color; ask first, never create events from a 6:30 routine unprompted.

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

Refresh this block from the saved answers plus new answers. Preserve earlier answered context and never replace it with a fresh unanswered question on a retry. Everything outside it — Chosen outcome, any legacy Top 3, Captured, Notes — is his and is never overwritten.

If he never answered, the block says so and carries the parked question:

```markdown
<!-- interview:start -->
*Asked 06:38 — not yet answered.*

> Q: You've got 09:00–14:00 blocked and one 🔴. Is that the whole day, or is something else landing?
<!-- interview:end -->
```

### 6. Choose one outcome, only after the interview

If `## Chosen outcome` is empty, propose one real item from both workspaces,
weighted: Urgent > blocks other work > at-risk (unbacked repos, expiring tokens)
> due today > stale-but-active. Include one short reason and a
`🔗 [OWE-nn](url)` or `🔗 [RES-nn](url)` link. Say if coverage is partial or
unavailable. Record Owen's choice in his words after he answers; do not claim
he completed a review or chose an item when he has not.

**Fit it to what he just told you.** A deep-work item on a day he described as
five hours of meetings and four hours of sleep is a plan that fails by 10am —
and now you have no excuse, because he said so.

Never overwrite an outcome he already wrote. If a legacy Top 3 exists, preserve
it and do not create a second planning section. Unattended runs may propose a
draft in the run output but leave the note's outcome unchanged, including when
empty.

### 7. Stamp and close

Set `interview-done: "<ISO timestamp>"` in frontmatter when he actually answered — that's what stops a re-run from re-interviewing. Leave it unset on an unattended fire.

Close by reading back the three things that changed versus the raw render. If nothing changed, say that too — it's evidence the render is good enough and the interview can get shorter.

## Rules

- **One question per message.** The rule the whole skill rests on.
- **Never ask what Linear, Calendar, or the vault already answers.** Present it for correction instead.
- **Only marked regions are regenerated.** `<!-- linear:* -->` and `<!-- interview:* -->`. Chosen outcome, any legacy Top 3, Captured, and Notes are his.
- **Marker ownership is strict.** This skill writes only `interview:start` through `interview:end`; daily-note owns Linear and mail-digest owns mail. Use the daily-note helper for marker updates.
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

- **The RES workspace render (added 2026-08-16).** Never fired from a scheduled run. The `linear-research` server, the Urgent/High-Backlog inclusion, and the "moved since last render" diff are all unexercised at 06:38. The diff depends on a prior `linear-res-last-success` cursor existing — a note created fresh that morning has none and must skip the line, not render everything as moved. An unknown or legacy-only cursor never counts as evidence of movement.
- **A live 6:30 fire.** The routine is created and the render half is inherited from a verified `daily-note`, but no morning has actually run interview-and-answer end to end yet. Expect the first real fire to pause on connector permission prompts.
- **Re-run guarding.** `interview-done` short-circuiting a second same-day run is written but unexercised.
- **The parked-question path** — asked at 6:30, answered at noon in a different session — is the most likely thing to be wrong.
