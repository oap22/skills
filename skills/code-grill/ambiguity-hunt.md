# Ambiguity Hunt

Run each check against the change. Each one with no answer yet becomes a frontier question. Skip a check only when the code or an earlier answer settles it, and say which.

Why this exists: a request like "the graphs should be different colors and not duplicate" sounds complete and is not. It does not say what a line represents, what happens on the 9th one, whether a color follows a run or a slot, or what "clear" clears. Building on that guess costs a round trip.

## Identity

What is the atomic unit Owen manipulates or the code operates on: a run, a metric, a run×metric pair, a request, a row, a file? Everything else is downstream of this, so ask it first.

## Language

Every load-bearing noun gets one meaning. "Account" could be Customer or User; "the model" could be a class, a checkpoint, or a table. If `GLOSSARY.md` defines it differently from how Owen uses it, ask which is right. If the code disagrees with what Owen says ("your code cancels whole Orders, but you said partial cancellation is possible"), show the line and ask.

## Interfaces

- Inputs: types, ranges, optional vs required, defaults.
- Outputs: shape, ordering, stability across versions.
- Errors: which ones exist, how the caller tells them apart, exit codes or status codes.
- Callers: who calls it today, who will call it, and whether any caller is outside this repo.

## State and lifecycle

- **Assignment stability**: when something is added to or removed from the middle, does everything else keep its color / position / ID / slot, or shift? Ask explicitly; "obviously stable" is often not what Owen means.
- **Removal**: how is each add undone? All-at-once and one-at-a-time are different features.
- **Reset scope**: what exactly a clear or reset returns to: empty, the default, or "the default for this part but not that part". This is the control most often left under-specified.
- **Persistence**: across a pane close, a process restart, a reboot, a deploy. Including whether a *cleared* state persists.

## Limits

Every finite resource (colors, slots, screen height, memory, rate limits, disk) needs a wraparound, a cap, or an expansion, and Owen picks. Also ask about empty input, one item, huge input, slow dependencies, and no network.

## Failure

What can fail, what the caller or user sees, what is retried and how often, what is lost, and whether a half-done operation can be resumed or must be rolled back.

## External writers

If a file, an agent, a cron job, another pane, or another user can set the same state, who wins, and does a manual action lock them out?

## Sentinels

Any magic entry ("auto", "latest", "all", `None`, `-1`) in a list of real things. How it resolves visibly, and what happens when it collides with the real thing it points at.

## Compatibility

Existing data on disk or in a database, existing configs, old clients, saved files. Does the change migrate them, read both forms, or break them? Who runs the migration?

## Proof

- The test seam: prefer an existing seam, as high as possible; the ideal number of seams is one. Confirm the seam with Owen.
- Prior art: similar tests in the repo to copy.
- The one end-to-end check that proves the behavior on the real target (CLI run, browser, device, cluster), not only a unit test.

## Owen's own invariant

Take his words literally and try to break them. He said "no duplicates": list every way a duplicate can arise and confirm each one is closed. He said "fast": get a number and a machine.
