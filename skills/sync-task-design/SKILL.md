---
name: sync-task-design
description: "Design a recurring task that mirrors a source of truth into another system without duplicating on re-run: a spreadsheet into a calendar, a form into a tracker. Use for \"keep these in sync\" or \"check this every day and put it in X\". Scheduler mechanics are local-routine."
---

# Scheduled Sync Task

A recurring sync runs in a fresh session every time, with no memory of the last run. The whole
design problem is making a stateless run produce the right result anyway.

## Steps

1. **Read the source before promising anything.** Real sources are full of placeholder rows,
   section headers, blank spacers, and stale historical blocks. Find the live section and the
   junk before scoping the work.

2. **Settle the ambiguities with the user.** Each of these silently determines whether the
   destination ends up clean or full of garbage to hand-delete:
   - **Scope** — which rows. Rarely all of them; usually one current section, usually future-dated only.
   - **Placeholder handling** — quote the actual strings found (`TBD`, `open for speaker`,
     `no event`, `Gap Week`) and ask which become records, which are skipped.
   - **Missing fields** — if the source has no times or durations, propose a default derived from
     historical rows and say plainly it is an inference.
   - **Deletion policy** — see rule below.
   - **Write-back** — confirm whether the source is ever written to. View-only access is common
     when the file belongs to someone else.

3. **Pick an ownership marker.** The task must distinguish its own records from ones the user
   created by hand. Put an unambiguous token in a field the destination preserves but ignores —
   a description, a notes field, a hidden column: `[<project>-sync]`. The task's instructions then
   read: *records this task owns carry this marker; never modify a record without it.*

4. **Pick a match key.** How a source row maps to an existing record. Choose the field **least
   likely to change**, because that is what survives an edit. For dated recurring events, match on
   **date**, not title — a renamed event keeps its date, so date-matching turns a rename into an
   update, while title-matching creates a duplicate and orphans the original.

5. **Seed the destination now, in the conversation.** Do the first sync by hand before scheduling
   anything, so the user can correct the format while someone is watching. Then schedule the task
   to maintain what you built.

6. **Write the reconcile procedure into the prompt.** Numbered, explicit:
   read source → read destination → match → create missing → update drifted → leave matches
   untouched → verify by re-reading → report.

7. **Save the schedule** using `local-routine`, then verify the readback.

## Rules

- **Reconcile, don't remember.** Never design the task to diff against a stored snapshot of
  yesterday's source. The state file drifts, gets deleted, or goes stale when a run is skipped, and
  then the task either duplicates everything or silently does nothing. A task that re-reads both
  sides and converges them is idempotent: re-running is harmless and a skipped run self-heals.

- **Default to never deleting.** If a source row disappears, leave the destination record and
  report it as orphaned. A row can vanish because it was cancelled *or* because someone was
  mid-edit when the task fired, and an unattended run should not make an irreversible call on
  ambiguous input. Offer full two-way mirroring only when asked, and say out loud that it deletes
  without confirming.

- **Tell the run what to do when nothing changed.** Instruct it to say so in one line. Otherwise
  every run emits a wall of text and the user stops reading them — which defeats the monitor.

- **Carry every identifier literally.** A fresh session cannot resolve "the spreadsheet we
  discussed". File IDs, destination IDs, which tool reads the source, real example strings from
  the filter rules.

- **Check the approval setting before calling it done.** A task that inherits "ask before acting"
  stalls on its first write with nobody there to approve. Where the scheduler exposes this, read it
  back; where automatic approval cannot be set programmatically, tell the user to switch it on and
  do not describe the task as working until they have.

- **If the scheduler evaluates cron in UTC, convert using the offset in effect at creation and say
  both times.** A UTC cron stored verbatim shifts by an hour relative to local time when DST ends;
  state it as "8am Central now, 7am once DST ends" rather than letting the user discover it in
  November. Local-time schedulers (the local Claude scheduler, per `local-routine`) do not need this.

- **Separate inference from fact in the report.** Defaults derived from historical rows are
  guesses; say which fields the source actually specified and which you filled in.

## Untested

- The reconcile loop was verified by construction and by re-reading the destination after the
  initial seeding run, not by observing a scheduled run detect and apply a real source change. The
  rename-handling behaviour of date-matching is reasoned, not yet exercised in production.
- Observed September 2026 against one cloud scheduler: a created task reported no
  `permission_mode`, meaning it inherits the creating conversation's approval setting. Treat as a
  dated observation about one harness, not a fact about others.
