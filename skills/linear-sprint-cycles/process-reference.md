# Process-doc reference

Material to adapt into a team's process doc. Replace the numbers with the team's own.

## Which field records what

| Field | Answers | Use it for |
| --- | --- | --- |
| Cycle | When are we working on this? | Every issue committed at planning; only the sprint lead sets it |
| Milestone | Which result does this feed? | Research, product or paper issues |
| Due date | Is there a hard outside deadline? | External deadlines only |
| Estimate | How big is it? | Every issue in a cycle |

## Estimates (Fibonacci)

| Points | Roughly |
| --- | --- |
| 1 | An hour or less |
| 2 | One evening |
| 3 | A few hours over the week |
| 5 | Most of one person's cycle |
| 8 | Too big: split before it enters a cycle |

Starting capacity = (hours per person per week × weeks per cycle), expressed in points, slightly under; if hours are unknown, ask. Switch to Linear's capacity dial after three finished cycles.

## Weekly retro + planning (two-week cycles)

**Sunday (or meeting day) that starts a cycle**
1. Retro on the cycle that ended (about 10 min): cycle graph, what got done, what rolled over and why, one change for next cycle.
2. Plan: pull issues from Backlog by milestone priority; each gets an estimate and an owner or "up for grabs"; stop at capacity.

**Mid-cycle meeting**
1. Mini retro (about 5 min): completed line vs target line; what is blocked.
2. Edit the cycle: behind → move lowest-priority work back to Backlog; ahead → pull in the next items. Scope changes on the graph are the record, not a failure.

**After each meeting:** a project update with health (on track / at risk / off track), one line why, and the retro notes.
**Before each meeting:** everyone updates their own issue statuses so the graph is accurate.

## Reading the graphs

| Graph | Where | Tells you |
| --- | --- | --- |
| Cycle graph | Cycles page, or open a cycle → Cmd/Ctrl + I | Gray = scope, dotted blue = target pace, yellow = started, solid blue = completed; at or above target = on track. Cycle success counts started issues as 25% |
| Capacity dial | Upcoming cycles | Whether the plan fits recent velocity (a member-count guess until 3 cycles finish) |
| Milestone progress | Project page | % done vs target date |
| Project updates | Project Updates tab | Health over time, with reasons |

## Cycle map

A table of cycle number → dates → focus → milestone reached. Mark break or exam cycles as light, and label every date that is a guess.
