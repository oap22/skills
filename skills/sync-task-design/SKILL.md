---
name: sync-task-design
description: "Design the reconcile logic for a recurring task that mirrors a source of truth into another system without duplicating on re-run (ownership marker, match key, no-delete default): a spreadsheet into a calendar, a form into a tracker. Use for \"keep these in sync\", \"check this every day and put it in X\", or a sync that duplicated or orphaned records; preferred over generic scheduled-sync skills. A one-way recurring report and scheduler setup or run diagnosis are local-routine."
---

# Sync Task Design

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
   - **Deletion policy** — see rule below. Also ask what happens when the user deletes a synced record by hand; the safe default is a tombstone: read deleted records too, where the destination exposes them, and do not recreate them.
   - **Hand edits** — which side wins when the user edits a synced record. Default: update only fields the source supplies (title, date) and never touch the rest (time, reminders, notes outside the marker); state the default.
   - **Write-back** — confirm whether the source is ever written to. View-only access is common
     when the file belongs to someone else.

3. **Pick an ownership marker.** The task must distinguish its own records from ones the user
   created by hand. Put an unambiguous token in a field the destination preserves but ignores —
   a description, a notes field, a hidden column: `[<project>-sync:<key>]`, carrying the match key so matching reads the marker, not editable fields. Prefer structured metadata the user cannot see or edit where the destination has it (Google Calendar private extended properties, filterable on list; keys over 44 characters are dropped silently). With no such field, append the marker to the title and tell the user. The task's instructions then
   read: *records this task owns carry this marker; never modify a record without it.*

4. **Pick a match key.** How a source row maps to an existing record. Use the source's own row or response ID if it has one. Otherwise choose the field **least
   likely to change**, because that is what survives an edit. For dated recurring events, match on
   **date**, not title — a renamed event keeps its date, so date-matching turns a rename into an
   update, while title-matching creates a duplicate and orphans the original. Check the source for repeated key values first; if one date holds several rows, key on date plus slot or order. If no field is stable and the source is writable, propose an ID column; if it is read-only, say a key change produces a new record plus an orphan, and have the report pair them as a possible move.

5. **Seed the destination now, in the conversation.** Do the first sync by hand before scheduling
   anything, so the user can correct the format while someone is watching. Then schedule the task
   to maintain what you built.

6. **Write the reconcile procedure into the prompt.** Numbered, explicit:
   read source → read destination → match → create missing (where the destination accepts a client ID, derive it from the match key so a retry returns "already exists", not a duplicate) → update drifted → leave matches
   untouched → verify by re-reading (duplicates, timezone offsets on both sides of a DST change, color or category IDs) → report. If a key matches more than one owned record, change none of them and report all.

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

- **Tell the run what to do when nothing changed.** Instruct it to say so in one line, counting known orphans rather than listing them again. Otherwise
  every run emits a wall of text and the user stops reading them — which defeats the monitor.

- **Carry every identifier literally.** A fresh session cannot resolve "the spreadsheet we
  discussed". File IDs, destination IDs, which tool reads the source, real example strings from
  the filter rules.

- **Do not call it done until local-routine's approval readback passes.** A sync stalls on its first
  write if it inherits "ask before acting"; if approval cannot be set programmatically, the user
  must switch it on first.

- **If the scheduler evaluates cron in UTC, convert using the offset in effect at creation and say
  both times.** A UTC cron stored verbatim shifts by an hour relative to local time when DST ends;
  state it as "8am Central now, 7am once DST ends" rather than letting the user discover it in
  November. If the conversion crosses midnight, shift the day-of-week fields too (8pm Central on weekdays is `0 1 * * 2-6` UTC). Local-time schedulers (per `local-routine`) do not need this.

- **Separate inference from fact in the report.** Defaults derived from historical rows are
  guesses; say which fields the source actually specified and which you filled in.

## Gotchas

- Observed September 2026 against one cloud scheduler: a created task reported no
  `permission_mode`, meaning it inherits the creating conversation's approval setting. Treat as a
  dated observation about one harness, not a fact about others.

## Untested

- The reconcile loop was verified by construction and by re-reading the destination after the
  initial seeding run, not by observing a scheduled run detect and apply a real source change. The
  rename-handling behaviour of date-matching is reasoned, not yet exercised in production.
