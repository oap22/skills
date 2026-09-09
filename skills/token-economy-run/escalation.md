# Escalation ladder

Three rungs, each used at most once per packet. The lead redoing a slice on the strong model at high effort is the most expensive path, so it is the last one.

| Rung | Who | When | Stop rule |
|---|---|---|---|
| 1 | `implementor` (cheap model, `--worker-effort`, usually `low`) | First attempt at every packet | Acceptance check fails twice after its own fixes: stop and report |
| 2 | `implementor-retry` (same model, `--worker-retry-effort`, one level up) | The same packet, re-sent once, unchanged unless the report exposed a packet defect | Same two-failure rule |
| 3 | The lead | Rung 2 stopped, or no retry rung was launched | Fix the packet (wrong entry points, wrong check, hidden dependency) or take the slice itself |

## Before climbing

Read the report's `Deviations` and `Blocker` lines first. Three outcomes call for fixing the packet rather than climbing:

- The implementor edited outside its owned paths, or needed to: the slice was not independent. Merge it into the neighbouring slice or take it in the lead.
- The blocker names a file or symbol the packet did not list: add the entry point. The corrected packet is a new packet and starts again at rung 1; it is not a re-send.
- The check command itself was wrong or flaky: fix the check in the lead before any rung sees it again.

## Counting

Each rung used counts as one packet escalated in the run log (`--escalated`). A packet that went rung 1, rung 2, then lead counts once, not twice; the log records how many packets needed rescue, not how many attempts they took.
