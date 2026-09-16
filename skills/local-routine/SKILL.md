---
name: local-routine
description: Schedule or update recurring agent work that needs local files or connected accounts. Use for "run this every morning", "set up a routine", or a recurring vault workflow. Use the current harness's native scheduler and verify its access before creating a task.
---

# Local Routine

A saved schedule is useful only if its execution environment can reach the files and accounts the work needs.

1. **Inspect the current scheduler and existing tasks.** Use the native scheduling tool available in this session. Match by name and prompt before creating; update the existing task to avoid duplicates. Do not assume Claude, Codex, or cloud schedulers share schemas, timezones, or connector access.
2. **Choose an environment from the actual dependencies.** Local vault paths require local access. Verify the intended Linear workspace and mail/calendar account; a connected service with the wrong account does not satisfy the dependency. In Codex, use a task-attached heartbeat by default, following the automation tool's current schema; use standalone project work only when requested.
3. **Write a self-contained prompt.** Include the skill, absolute paths, account/team identifiers, timezone, ownership markers, expected output, and permitted mutations. Resolve relative dates at run time. State how to report partial failures without presenting missing data as an empty queue. Preserve the user's authorization and notification intent. Do not put credentials in the prompt.
4. **Save the requested schedule.** Interpret it in the user's timezone (America/Chicago unless overridden), using the tool's supported format. Preserve unrelated existing fields on updates. Use a native one-shot mechanism for one-shot requests; never temporarily replace a recurrence to force a test run.
5. **Verify the saved result.** Read back the task ID, prompt, enabled state, timezone, and recurrence. Check the next run when exposed. Report setup separately from execution: a task that saved successfully has not yet proved its first run works.
6. **Record only what is in scope.** Update a project runbook if this setup includes it. Write harness memory only on an explicit user request.

For monitors, stay quiet while state is unchanged or non-actionable; notify on meaningful change, completion, failure, or required user action unless the user requested periodic reports. Prefer the scheduler's notification mechanism over a second push notification.

## Observed Claude-specific pitfalls

The local Claude scheduler observed in August 2026 used local-time cron and deterministic jitter; cloud routines had different access and timing semantics. A missing connector made a healthy-looking schedule unable to do its job. These are dated observations, not facts about other harnesses or their current versions.

A prior local tool exposed create/update/delete/list but no run action. If the current tool still lacks one, use its supported UI path; do not change recurrence to a near-future one-shot, which previously cleared the cron and disabled the routine afterward. Verify current app-open and missed-run behavior rather than promising replay or catch-up from this old observation.
