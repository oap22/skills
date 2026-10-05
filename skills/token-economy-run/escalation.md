# Escalation ladder

Three rungs, each used at most once per packet. The lead redoing a slice on the strong model at high effort is the most expensive path, so it is the last one.

| Rung | Who | When | Stop rule |
|---|---|---|---|
| 1 | `implementor` (cheap model, `--worker-effort`, usually `low`) | First attempt at every packet | Acceptance check fails twice after its own fixes: stop and report |
| 2 | `implementor-retry` (same model one effort level up via `--worker-retry-effort`, or a stronger model via `--worker-retry-model`) | The same packet, re-sent once, unchanged unless the report exposed a packet defect | Same two-failure rule |
| 3 | The lead | Rung 2 stopped, or no retry rung was launched | Fix the packet (wrong entry points, wrong check, hidden dependency) or take the slice itself |

## Before climbing

Read the report's `Deviations` and `Blocker` lines first. Four outcomes call for fixing the launch or packet rather than climbing:

- The dispatch failed before any work (unknown model, no access): `preview` does not validate model aliases. Relaunch with an available alias, or take the slice in the lead. No rung is used.
- The implementor edited outside its owned paths, or needed to: the slice was not independent. First restore every path outside its owned set that another packet or the lead owns, then check `git status` against all owned sets. Merge it into the neighbouring slice or take it in the lead.
- The blocker names a file or symbol the packet did not list: add the entry point. The corrected packet is a new packet and starts again at rung 1; it is not a re-send.
- The check command itself was wrong or flaky: fix the check in the lead before any rung sees it again.

## Counting

A packet that needed rung 2 or rung 3 counts as one packet escalated in the run log (`--escalated`); a corrected packet that restarts at rung 1 is a new packet in `--packets`. A packet that went rung 1, rung 2, then lead counts once, not twice; the log records how many packets needed rescue, not how many attempts they took.
