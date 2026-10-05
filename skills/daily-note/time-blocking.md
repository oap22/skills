# Daily Note: time blocking

Only on explicit request. This is the one step that **writes outside the vault** — treat it conservatively.

**Find the gaps.** Working window **08:00–20:00** America/Chicago. Respect busy all-day events and `OUT_OF_OFFICE`; ignore only events explicitly marked free. Leave a **15-minute buffer** each side of an existing event.

**Size the outcome first.** Use an explicit duration when present. Story points are not hours; convert only with a team-provided mapping, otherwise estimate from scope and label it:

| Size | Looks like | Examples |
|---|---|---|
| **30 min** | one bounded action, obvious done state | send an email, reissue a token, add a git remote |
| **60 min** | bounded but multi-step, or writing something short | a literature note, inbox triage |
| **90 min** | real focus, edges not fully known | benchmark two models, build out a workflow |
| **open-ended** | cannot finish in a day | train a model, reverse-engineer a repo |

**Open-ended work gets one 90-minute block to *start*** — title it `🎯 RES-nn — start: <title>` so the block promises what it can deliver.

**Fit it** in the earliest viable gap that starts after now. Full size or shrink by at most 30 minutes; below that skip rather than cram. Never overlap an existing event, never run past 20:00. Put the estimate in the chosen-outcome line (`— ~30m`) so Owen can correct it; repeated corrections are the cue to set a real `estimate` in Linear.

**Create with an idempotency marker.** Summary `🎯 RES-nn — <short title>`; the `🎯 RES-nn` prefix is what the next run keys on.

```
summary:     🎯 RES-5 — Reproduce the baseline on ImageNette
startTime / endTime / timeZone: America/Chicago
description: <one-line reason from the chosen outcome> + the Linear URL
eventType:   DEFAULT
availability: AVAILABILITY_BUSY
colorId:     <from .system/calendar-conventions.md>
```

Color comes from `.system/calendar-conventions.md` (focus blocks inherit their category; RES issues are Research → Tangerine `6`, not Lavender — that is reserved for AI Club meetings). Never leave `colorId` unset; the default renders as School. Use `DEFAULT`, not `FOCUS_TIME`, which can auto-decline real invitations.

**Before creating anything, re-list today's events and skip any `RES-nn` that already has a `🎯 RES-nn` block.** The routine has jitter and gets run by hand too.

If nothing fits, create nothing and say so. A day with no room is a real answer.
