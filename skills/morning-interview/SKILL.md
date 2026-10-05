---
name: morning-interview
description: "Have daily-note render today's note, then interview Owen one question at a time about capacity, unscheduled commitments, and priorities. Use for \"morning interview\", \"morning check-in\", \"interview me about today\", or a scheduled morning run. A read-only summary is day-check; a render with no interview is daily-note."
---

# Morning Interview

Every marker write goes through the vault helper under its `note_lock` (`.system/locks/daily-note.lock`); no whole-file fallback, and duplicated or unbalanced markers mean preserve the file and report. Scheduling statements below are setup notes: inspect the live task before reporting or changing it.

The connectors know what's *scheduled*. They do not know what's coming — a ride to catch, a professor who might reply, a lab due but never filed, four hours of sleep. This skill has `daily-note` render the machine-knowable half, then asks about the rest.

**Vault:** `~/Owen's Awesome Vault`
**Note path:** `School/Daily TODO/YYYY-MM-DD.md`
**Render, Linear scope, lock, marker ownership, cursors, environment:** `../daily-note/SKILL.md` is the single render contract; this file does not restate it.

This skill owns only `<!-- interview:start -->` … `<!-- interview:end -->`. `daily-note` owns `linear` and its `linear-*` frontmatter fields; `mail-digest` owns `mail`. An interview-only write never advances the `linear-*` fields.

## The two ways this starts

**Unattended (the scheduled fire).** Nobody is answering yet. A missed fire can start hours late, once, when the app opens or the Mac wakes: resolve today's date, render today, and stamp the real ask time. Render, write the brief, ask the *first* question in the note and in the run output, and stop. Do not fabricate answers or present a guessed Chosen outcome as agreed. A morning where nobody answers still leaves a fully rendered note.

**Attended (he invoked it, or replied to the fire).** Read the interview block first. Render if `linear-rendered-at` is not today, then run the interview live. A parked question is the first question: keep its Asked time, skip threads whose time has passed, and re-derive any outcome proposal (the scheduled run's output is not visible here).

If the note's interview block already says `answered`, don't re-interview — say so and offer a refresh of the rendered block only.

## Steps

### 1. Resolve today

```bash
TZ=America/Chicago date +%Y-%m-%d
```

Never hardcode, never trust a date from earlier in the conversation.

### 2. Render the day

Read `../daily-note/SKILL.md` and perform its **render-only** steps (1–3, 6). Do not run its time-blocking step, change Captured, or fill Chosen outcome before the interview. If the skill is unavailable, report the missing dependency and present the available day context in chat; do not reconstruct a second rendering contract.

### 3. Show the day back before asking anything

Open with the picture, not a question. Read the existing `## Mail` block without rerunning the mail sweep. Include yesterday's Chosen outcome if it is not marked done, and any delivery change, waiting-on-you, or must-know item alongside total scheduled hours, the largest free gap, count of urgent issues, and anything due today. Say when the mail block is absent, stale, or reports an unavailable connector. Two or three lines.

Same principle as `deep-interview`: **never ask what you can read.** "You've got 09:00–14:00 blocked and one 🔴 — is that the whole day?" is worth answering. "What's on today?" makes him recite his own calendar.

### 4. Interview — one question per message

**Never batch.** A numbered list of six questions gets six shallow answers. Keep the framing to a line.

Let each answer choose the next question. Start with the biggest hole in the render. Territory, as threads not a checklist:

- **Unscheduled fixed time** — rides, commutes, departure times that aren't events
- **Today's real deadline** — the thing due that is on neither Calendar nor the note
- **Waiting on** — replies expected today, from whom, what stalls without them
- **Capacity** — sleep, energy, anything physical that shrinks the day
- **The one thing** — if only one item lands, which
- **Anything he already knows will go wrong**

Stop when the answers stop changing the plan. Six good questions beat fifteen dutiful ones.

### 5. Write as you go, not at the end

After each answer, file it. Long conversations get compressed and unwritten answers are lost.

| Answer | Destination |
|---|---|
| Fixed time not on Calendar | a `## Schedule` row, Source `🗣 interview` (no Calendar link) |
| New actionable | `## Captured` as a checkbox — **not** a Linear issue, in any workspace |
| Waiting-on / context / capacity | the `<!-- interview:start -->` block |
| A real commitment to someone | `30-Brain/Commitments/` per `30-Brain/Commitments/README.md` |

The helper CLI exposes only the `mail`, `interview`, and `linear` regions. No locked adapter for Schedule rows or Captured checkboxes exists yet (checked 2026-10-05). Keep the answer in the interview block and report Schedule/Captured persistence as blocked — never an unlocked whole-file write, never a dropped answer.

If a piece of fixed time is load-bearing — a game, a ride, a window he can't be scheduled into — **offer to put it on Calendar** via `calendar-block` so it gets the right color. Ask first; a 6:30 routine never creates events unprompted.

The interview block lives under its own heading, below `## Schedule`:

```markdown
## Morning Check-in

<!-- interview:start -->
*Asked 06:38 · answered 07:12.*

**Capacity** — ~5h sleep, running on short rest.
**Unscheduled** — ride to campus leaves 08:20, not on Calendar.
**Waiting on** — Dr. Vance reply re: undergrad research; nothing else blocks on it.
**Expects to go wrong** — the 14:15 drive will eat the afternoon block.
<!-- interview:end -->
```

Refresh this block from saved answers plus new ones. Never replace answered context with a fresh unanswered question on a retry. If he never answered:

```markdown
<!-- interview:start -->
*Asked 06:38 — not yet answered.*

> Q: You've got 09:00–14:00 blocked and one 🔴. Is that the whole day, or is something else landing?
<!-- interview:end -->
```

### 6. Choose one outcome, only after the interview

Apply `daily-note` step 4, fitted to what he just said — a deep-work item on a day he described as five hours of meetings and four hours of sleep fails by 10am, and now you know it. Once he agrees to the outcome, write one line in the interview block: when and where it starts (a free gap from the render), and "If <what he expects to go wrong>, then <fallback>". Never overwrite an outcome he wrote. Unattended runs propose in the run output only and leave the note's outcome unchanged, even when empty.

### 7. Stamp and close

The block's `answered HH:MM` line is the done signal, written only when he answered. Frontmatter `interview-done` has no locked helper path yet; report it as not written.

Close by reading back the three things that changed versus the raw render. If nothing changed, say so — evidence the render is good enough and the interview can get shorter.

## Rules

- **One question per message.**
- **Never ask what Linear, Calendar, or the vault already answers.** Present it for correction.
- **Only the interview region is this skill's to regenerate.** Chosen outcome, legacy Top 3, Captured, and Notes are his; `linear` and `mail` belong to their skills.
- **Never check off a rendered Linear issue in the vault.** State changes go to Linear.
- **A 6:30 routine does not write to Linear.** It captures; promotion is Owen's decision at triage (`vault-triage`).
- **"Skip" ends a thread instantly.** Health, money, and sleep get asked plainly and dropped without friction.
- **Don't turn it into advice.** A line or two of implication, not a plan.
- **Resolve the date at runtime**, `America/Chicago`. **Never delete vault content**; ask first.

## Scheduling

Task `morning-interview`, `30 6 * * *` America/Chicago, local scheduler only (see `local-routine`); found disabled 2026-10-05 (last run 2026-09-28), so inspect it before calling it live and re-enable only on request. Its saved prompt should only invoke this skill; the 2026-09-18 copy carries drifted fallback steps (`linear-synced`, unlocked Schedule writes). `daily-note-render` stays disabled.

## Gotchas

- The local scheduler fires only while its host app is open and the Mac awake; a miss gets one catch-up at next launch or wake, possibly alongside other routines' catch-ups, so the mail block may be stale; reported times include deterministic jitter.
- **Verify proper nouns against written sources.** He dictates; names arrive garbled.

## Untested

- No morning has run interview-and-answer end to end from the scheduled fire; a manual-approval run stalls at its first unapproved tool and writes nothing; check the task's approval mode per local-routine.
- The `answered` short-circuit of a same-day re-run is unexercised.
- The parked-question path — asked at 6:30, answered at noon in a different session — is the most likely thing to be wrong.
