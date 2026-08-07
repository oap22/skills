---
name: calendar-block
description: Create or recolor Google Calendar events using Owen's category color scheme, padding real-world commitments into blocks that actually protect the time, and fit undated tasks into whatever free time he actually has. Use when he says "block out", "put X on my calendar", "I can't do anything then", "nothing before 10", "add this to my calendar", "when am I free", "fit this in", "find me time for", or when any other skill needs to write an event.
---

# Calendar Block

Owen's calendar is the system of record for fixed time. Every event carries a category color so a week reads as a breakdown at a glance. This skill is the single place that knows how.

**Calendar:** `oap1722@gmail.com` · timezone `America/Chicago`
**Source of truth:** `$HOME/Owen's Awesome Vault/.system/calendar-conventions.md` — read it before writing anything; it may have drifted ahead of this file.

## The color scheme

| Category | `colorId` | Color |
|---|---|---|
| School — classes, homework, study | `9` | Blueberry |
| Research — Wright, Wang, lab, papers | `6` | Tangerine |
| Work — employment, shifts | `5` | Banana |
| Soccer — practice, games, alumni | `10` | Basil |
| Fitness — gym, climbing, runs | `2` | Sage |
| Meals — dinner, reservations, cooking | `4` | Flamingo |
| Clubs — AI Club, FOSS, website dev | `1` | Lavender |
| Personal — appointments, errands | `8` | Graphite |
| Social — friends, shows, downtime | `3` | Grape |
| Deadlines — due dates, exams | `11` | Tomato |
| Travel / unavailable — transit, walls | `7` | Peacock |

**Never omit `colorId`.** Google's default is Blueberry, which is indistinguishable from School. An uncolored event is a bug.

When two fit, pick the one that would make Owen decline the other. Soccer beats Fitness. Deadlines beat everything.

## Steps

### 1. Resolve the date

```bash
date +%Y-%m-%d
```

Never trust a date from earlier in the conversation. "Tomorrow" is relative to now, not to when the session started.

### 2. Check what's already there

List events for the target day (`orderBy: startTime`, `timeZone: America/Chicago`) **before** creating anything. Two reasons: you need to report conflicts, and a repeated request shouldn't produce a duplicate event.

If something already covers the window, say so and ask before adding a second block.

### 3. Classify

Pick the category from the table. Classify by **what the time is**, not who requested it — a meeting with a professor about coursework is School; about a paper is Research.

### 4. Pad the block

Owen states the event. You state the wall.

- "Game around 6:30" → block **6:00–8:30**. Travel, warmup, and the thing running long are all real.
- Put his stated time in the `description` so the padding is visible and correctable: `"Game around 6:30 — block covers travel/warmup on either side."`
- Err toward more padding for anything with travel, and less for anything at home.

### 5. A constraint is an event

"Nothing before 9:45", "I'm out until noon", "don't schedule me Friday afternoon" — these are not notes, they are events. A constraint that lives only in conversation gets scheduled over by the next run of `daily-note`.

Create a real block, `00:00` to the stated time for a wake-up constraint, colored `7`, titled for what it is (`Unavailable — sleeping in`).

### 6. Create

```
summary:      <plain title, no emoji unless it's an agent focus block>
startTime / endTime / timeZone: America/Chicago
availability: AVAILABILITY_BUSY
colorId:      <from the table>
description:  <what Owen actually said, if you padded>
eventType:    DEFAULT
```

`AVAILABILITY_BUSY` always. A block that doesn't block is decoration.

Use `DEFAULT`, never `FOCUS_TIME` — focus-time events can auto-decline real invitations.

### 7. Report

Say what landed, what it conflicts with, and what the remaining free window is. "Your free window is 9:45 AM–6:00 PM" is the sentence Owen actually uses.

## Recoloring existing events

When asked to bring old events in line: list them, group by summary, propose the mapping, **and get a yes before writing.** Recurring events recolor every instance — that is a lot of visual change at once, and it is not obviously reversible.

Never recolor an event Owen didn't create (Gmail-derived events, invitations from others).

## For other skills

`daily-note` and `morning-interview` create focus blocks. Those inherit the **Linear project's** color, not a fixed one:

| Linear project | `colorId` |
|---|---|
| School | `9` |
| Research | `6` |
| Personal | `8` |

## Rules

- **Never delete a calendar event.** Ask. Deletion is the one action here with no undo.
- **Never edit an event Owen didn't create.**
- **Never leave `colorId` unset.**
- **Pad, then say you padded.** Silent padding trains him to distrust the block.
- **Re-list before creating** — the same request twice should not produce two events.

## Known state

- **Cognex ended August 2026.** The recurring `In-Person Work` / `Remote Work` events (Banana) are stale leftovers. Banana stays reserved for future employment; don't reassign it.
- Pre-2026-08-07 events were never colored systematically. Don't infer the scheme from calendar history.

## Untested

- **Recoloring recurring events has never been run.** Whether `update_event` on a recurrence instance ID colors the single instance or the whole series is unverified — check on a low-stakes series first.
- **The Deadlines (`11`) and Social (`3`) categories have no events yet.** They're allocated, not exercised.
- **Padding heuristics are judgment, not measured.** The 30-minutes-each-side default came from one soccer game on 2026-08-07.
