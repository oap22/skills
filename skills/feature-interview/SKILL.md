---
name: feature-interview
description: "Interview the user one question at a time until a feature's behavior is fully pinned down, then write the spec the implementation is held to. Use for \"spec this out\", \"nail down what I want\", or an under-specified feature. Research questions go to research-interview."
---

# Feature Interview

Reach complete shared understanding of a feature's **behavior** before writing code. The output is a spec that names every state, transition, and edge case, so the implementation has a contract to satisfy instead of a vibe to guess at.

The trigger is usually a rebuild. A feature request like "the graphs should be different colors and not duplicate" sounds complete and isn't: it doesn't say what a line represents, what happens on the 9th one, whether a color follows a run or a slot, or what "clear" clears. Building on that guess costs a round trip. This skill spends five minutes to avoid it.

**Not for research.** Experiments, hypotheses, and success criteria go to `research-interview`. This skill is for behavior a user will click on.

## The Standard

The interview is done only when *both* are true:

1. **You can state the whole behavior back and the user changes nothing.** Any correction means you weren't done — absorb it and restate. Loop until the restatement survives untouched. Explicit approval of the concrete restatement suffices; do not require verbatim repetition or restart after a minor correction.
2. **Every invariant the user asked for is provably unbreakable, or you know exactly where it breaks and the user chose that.** "All different colors" is not a spec until you have asked what happens when there are more runs than colors.

## The Rules That Make It Work

**One question per message.** Two only when genuinely coupled — a mechanism and its immediate consequence, where answering one alone would be meaningless. Six questions in a call gets six shallow answers.

**If the harness exposes a structured question tool, use it with concrete options; otherwise ask in chat.** Feature behavior is almost always enumerable: 2–4 real alternatives, each one something you would actually be willing to build. "Other" covers the rest. Never offer an option you'd argue against — that's a fake choice that wastes a turn.

**Put a state diagram with every option** (in the tool's per-option preview field if it has one, inline in chat if not). This is what makes the difference. Each option shows the *before → action → after* in monospace, using the app's real vocabulary:

```
before:  [x] auto → run-a (blue)
new run-b lands
after:   [x] auto → run-b (amber)
         [x] run-a          (blue, now pinned)
```

The user is choosing between futures they can see, not between sentences they have to simulate. Options that read as near-identical prose become obviously different once drawn. Write previews for the *consequence*, not the mechanism — show what ends up on screen.

**Never ask what you can read.** Open the code first. Know what the feature does today, what the data model is, and which of the user's complaints are already fixed — then say so, and ask only about what's genuinely undecided. Reporting "I already fixed one of the two duplicate sources; here's the other one" is worth more than any question.

**Follow the consequence, not a checklist.** Every answer opens the next question. Keep auto-follow → what happens to the run it was showing → what clicking its now-dimmed row does. Three questions deep on one thread beats one question each on three threads.

## The Ambiguity Hunt

Run each of these against the feature. Each one that has no answer yet is a question:

- **Identity** — what is the atomic unit the user manipulates? (a run? a metric? a run×metric pair?) Everything else is downstream of this, so ask it first.
- **Assignment stability** — when something is added or removed from the middle, does everything else keep its color / position / slot, or shift? Ask explicitly; "obviously it should be stable" is often not what the user means.
- **Overflow** — what happens past the limit? Every finite resource (colors, slots, screen height) needs a wraparound, a cap, or an expansion, and the user has to pick.
- **Removal** — how do you undo each add? All-at-once and one-at-a-time are different features; ask about both.
- **Reset scope** — what exactly does the clear/reset control return to: empty, the default state, or "the default for this part but not that part"? This is the single most reliably under-specified control in any UI.
- **Persistence** — across a pane close, an app restart, a machine reboot. Including whether a *cleared* state persists.
- **External writers** — if a file, an agent, or another pane can set the same state, who wins, and does a manual action lock them out?
- **Sentinels** — any magic entry ("auto", "latest", "all") sitting in a list of real things. Ask how it resolves visibly, and what happens when it collides with the real thing it points at.
- **The user's own invariant** — take their words literally and try to break them. They said no duplicates: enumerate every way a duplicate can arise, and confirm each one is closed.

## Closing

1. **Read the spec back** as numbered behavior statements, grouped by surface. Not a summary — a specification, in the app's vocabulary, that someone else could implement from.
2. **Separate what you decided yourself.** List the routine judgment calls you made rather than asking (naming, ordering, exact pixel affordances) under a heading the user can skim and veto.
3. **Write it to a file** before implementing — `.scratch/prd-<feature>.md` or wherever the project keeps specs. The spec outlives the conversation and the implementation gets checked against it.
4. **Then hand the spec to implementation; get explicit go-ahead first unless already authorized.** Report against the spec's numbered points so the user can verify coverage without reading the diff.
