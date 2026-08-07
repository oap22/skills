---
name: day-check
description: Answer "what do I need to do today?" in chat — read-only, from Calendar and Linear, weighted to whatever time is actually left. Use when Owen asks "what do I need to do", "what should I work on", "what's most important right now", "what's left today", "am I forgetting anything", "do I have anything coming up", or asks about his day in passing without asking for the note to be built.
---

# Day Check

A question, not a routine. Owen asked what's on his plate — answer it in chat, in seconds, and touch nothing.

**Read-only. Always.** No note is written, no Linear issue is changed, no calendar event is created. If the answer implies work — block that time, file that issue, refresh the note — *offer* and wait. The whole value of this skill is that asking is free.

**Not this skill:** if he asks to build or refresh the daily note, that's `daily-note`. If it's the 6:30 routine or he wants to be interviewed, that's `morning-interview`. If the question is about mail, that's `mail-digest`. Hand off rather than doing a partial version.

**Vault:** `$HOME/Owen's Awesome Vault` · **Linear:** team **Owen's Operations** (`OWE`), projects School / Research / Personal

## Steps

### 1. Anchor to now, not to today

```bash
date "+%Y-%m-%d %H:%M %A"
```

`America/Chicago`. **The current time is the whole point** — at 15:00 a list of this morning's events is noise. Everything below is filtered to what's still ahead.

### 2. Pull the three sources

In parallel where possible; none depends on another.

- **Calendar** — today's events, `orderBy: startTime`, `timeZone: America/Chicago`. Drop `WORKING_LOCATION` and `BIRTHDAY`. Keep all-day events (a due date shows up this way) but don't count them as occupied time. Note which are `🎯 OWE-nn` focus blocks — those are self-assigned and moveable, unlike a class or a meeting.
- **Linear** — `assignee: "me"`, states Todo and In Progress, `fields: ["id","title","project","priority","status","dueDate","url"]`. Priority is **1 = Urgent … 4 = Low, 0 = None** — never sort naively.
- **Today's note** — `School/Daily TODO/YYYY-MM-DD.md` if it exists. Read the `## Top 3` and `## Captured` sections only. A Top 3 he wrote himself outranks anything inferred; Captured holds things that exist nowhere else yet.

If a source is unreachable, say which one and answer from the rest. A partial answer now beats a complete one after a reconnect.

### 3. Answer the question he actually asked

Three shapes, and they get different answers:

| He asked | Give him |
|---|---|
| "What do I need to do today?" | Fixed commitments still ahead, then the handful of open items that matter. Comprehensive-ish. |
| "What should I work on / target?" | **One recommendation**, plus two alternates. Not a list — a call. |
| "Anything coming up / am I forgetting something?" | Only the surprising: something starting soon, a due date today, an item that's been sitting. Silence is a valid answer. |

**Weighting for a recommendation**, in order: due today or overdue → Urgent → blocks something else → fits the gap that actually exists before the next fixed event → has been stale longest. A 90-minute recommendation with 40 minutes until his next class is a bad answer no matter how important the issue is.

### 4. Keep it short

Chat, not a document. Target **under 150 words**. Lead with the next fixed thing and how long until it starts, then the work. Use `OWE-nn` ids so he can act, skip tables unless there are more than about six items, and never render a checklist — nothing here is checkable.

Say the time remaining explicitly (`2h10m until Physics`), because that's the number he's actually deciding against.

If there is genuinely nothing — no events left, no open urgent work — **say so plainly**. Manufacturing a suggestion to seem useful is the main way this skill goes wrong.

## Rules

- **Never write anything.** Vault, Linear, Calendar — all read-only, every time. Offer, don't act.
- **Filter to what's ahead.** Past events appear only if he asked what he already did.
- **A hand-written Top 3 wins.** If he already decided this morning, the answer is his own list plus what's changed since — not a fresh ranking that quietly overrides him.
- **Don't re-derive the day on a follow-up.** Within one conversation, reuse what was already pulled; re-pull only if he says something changed or enough time has passed to matter.
- **Don't promote Captured items to Linear here.** Mention them, and offer `vault-to-linear` if he wants them real.
- **Focus blocks are suggestions, not commitments.** A `🎯 OWE-nn` block he's blown past is fine — mention it, don't scold, and don't reschedule it unasked.

## Untested

- Never run. Written 2026-08-07 from Owen's description of wanting a lightweight ask-anytime alternative to the full digest.
- The three answer shapes in step 3 are a guess at how he actually asks. If he only ever asks one way, collapse the table.
- The under-150-word budget is unverified against a day with a full calendar *and* a long Linear queue — that's the case where it will want to sprawl.
- Overlap risk with `daily-note` and `morning-interview` on routing: all three sit near "what's on today". If the wrong one fires, the fix is sharpening the trigger phrases here, not adding steps.
