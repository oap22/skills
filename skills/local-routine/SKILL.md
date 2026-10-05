---
name: local-routine
description: "Schedule, update, disable, or diagnose recurring agent work that needs local files or connected accounts, using the current harness's durable local scheduler after verifying its access; cloud schedulers cannot reach local files. Use for \"run this every morning\", \"set up a routine\", \"my routine didn't run\". A repeat inside the current session is not a routine. Reconcile design lives in sync-task-design."
---

# Local Routine

A saved schedule is useful only if its execution environment can reach the files and accounts the work needs.

1. **Inspect the current scheduler and existing tasks.** Use the native durable scheduler available in this session; a session-scoped one that expires or needs an open session cannot hold a recurring routine, and a cloud one only fits work with nothing local. If none is exposed, say so and stop. Match by name and prompt before creating; update the existing task to avoid duplicates. If the match is disabled, say so and ask before re-enabling it; it may have been retired on purpose. Do not assume Claude, Codex, or cloud schedulers share schemas, timezones, or connector access.
2. **Choose an environment from the actual dependencies.** Local vault paths require local access. Verify the intended Linear workspace and mail/calendar account; a connected service with the wrong account does not satisfy the dependency. Prove each dependency with one read from this session that shows the path or account; if one fails, do not save, and report what is missing. When the task edits a git repo, choose an isolated worktree unless it must change the live checkout. In Codex, attach the schedule to the current thread by default, following the scheduling tool's current schema; use a standalone task only when requested.
3. **Write a self-contained prompt.** Include the skill, absolute paths, account/team identifiers, timezone, ownership markers, expected output, and permitted mutations. Resolve relative dates at run time, and say what to do when a run starts late (a catch-up after sleep or app launch). State how to report partial failures without presenting missing data as an empty queue. Preserve the user's authorization and notification intent. Do not put credentials in the prompt. The `mail-digest` task is a working reference.
4. **Save the requested schedule.** Interpret it in the user's timezone (America/Chicago unless overridden), using the tool's supported format. Preserve unrelated existing fields on updates. Use a native one-shot mechanism for one-shot requests; never temporarily replace a recurrence to force a test run.
5. **Verify the saved result.** Read back the task ID, prompt, enabled state, recurrence, and approval mode. If timezone is not shown, infer it from the next run against the cron and label jitter-shifted times as jitter. Confirm the permission or sandbox mode lets the work run unattended (a manual-approval run stalls), and remove connectors or write access the task does not need. Report setup separately from execution: a task that saved successfully has not yet proved its first run works. Check the run history after the first fire, or use run-now when the task's mutations are safe to repeat.
6. **Record only what is in scope.** Update a project runbook if this setup includes it. Write harness memory only on an explicit user request.

For monitors, stay quiet while state is unchanged or non-actionable; notify on meaningful change, completion, failure, or required user action unless the user requested periodic reports. Prefer the scheduler's notification mechanism over a second push notification.

## Gotchas

The local Claude scheduler observed in August 2026 used local-time cron, ran only while the app was open (a missed run could fire at next launch), and added deterministic jitter (`15 6 * * *` ran at 06:22); cloud routines had different access and timing semantics. A missing connector made a healthy-looking schedule unable to do its job. These are dated observations, not facts about other harnesses or their current versions.

If the scheduler has no run-now action, use its supported UI path. Do not fake a run by switching recurrence to a near-future one-shot: that can clear the cron and leave the routine disabled. Verify app-open and missed-run behavior before promising replay or catch-up.
