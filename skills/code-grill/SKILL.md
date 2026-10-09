---
name: code-grill
description: "Grill Owen in rounds about any planned code change (feature, refactor, CLI, API, architecture) until there is a shared understanding, keeping GLOSSARY.md and ADRs current, then write the spec sheet the implementation is held to. Use for \"grill me on this\", \"spec this out\", \"nail down what I want\", or a change whose behavior or design is still open. ML training runs go to run-grill; project purpose to vision-interview; plan-then-ship runs its own spec step."
---

# Code Grill

Reach a complete shared understanding of a code change before any code is written. The output is a spec sheet that names every behavior, state, edge case, and decision, so the implementation has a contract to satisfy instead of a vibe to guess at. Ask as many questions as it takes. Owen's fatigue or a long session is not a reason to stop; an empty frontier is.

Adapted from Matt Pocock's `grill-with-docs` (grilling + domain-modeling + to-spec), MIT, Copyright (c) 2026 Matt Pocock: https://github.com/mattpocock/skills.

**Not for research.** Experiments and training runs go to `run-grill`. **Coursework:** in professor mode the spec records only Owen's decisions; propose no design that solves the assignment.

## Steps

1. **Read first.** Open the code, `GLOSSARY.md` (or `GLOSSARY-MAP.md`), `docs/adr/`, `docs/specs/`, and any tracker issue Owen names. Know what the code does today, what the data model is, and which parts of the request already work. Open with what you believe and ask what is wrong. With no code yet, the first round asks the identity question and uses Owen's own nouns.
2. **Grill in rounds** (below) until the frontier is empty.
3. **Write as you go** (below): spec draft, glossary terms, and ADRs the moment they settle.
4. **Close** (below): restate, separate your own calls, get confirmation, hand off.

## Rounds

Map the change as a **design tree**: each decision branches into the decisions that hang off it. The **frontier** is every open decision whose prerequisites are settled. Ask the whole frontier in one round, numbered, each with your recommended answer, then wait.

```
❓ **Q1** - **<title>**: <question, with the real options and a state diagram when behavior differs>

➡️ <recommended answer, one-clause reason>

---

❓ **Q2** - ...
```

- Word each question so "yes" accepts the recommendation. Owen can answer "all yes", "yes except Q3: ...", or per number.
- A question whose answer depends on another question in the same round goes in a later round.
- Each answer reshapes the tree. Recompute the frontier; follow consequences three deep on one thread before you call a branch done.
- If the frontier is one question with enumerable answers and the harness has a structured question tool, use it with 2-4 options and per-option previews. Never offer an option you would argue against.
- **Facts are your job; decisions are Owen's.** Never ask what the code, docs, or tools can answer. Look it up, or send a subagent when it is slow; only the questions downstream of a running lookup wait for it.
- **Draw behavior.** When options differ in what the user or caller sees, show *before → action → after* in monospace with the app's real vocabulary. Draw the consequence, not the mechanism:

```
before:  [x] auto → run-a (blue)
new run-b lands
after:   [x] auto → run-b (amber)
         [x] run-a          (blue, now pinned)
```

## The Ambiguity Hunt

Run each against the change. Each one with no answer is a frontier question. Read [ambiguity-hunt.md](ambiguity-hunt.md) for the full list with examples; the short form:

- **Identity**: the atomic unit being manipulated. Ask first; everything is downstream.
- **Language**: every load-bearing noun matches `GLOSSARY.md` or gets a canonical term now.
- **Interfaces**: inputs, outputs, errors, and who calls it.
- **State and lifecycle**: create, change, remove, reset scope, persistence across restarts.
- **Limits**: overflow, empty, huge, concurrent, slow, offline.
- **Failure**: what fails, what the caller sees, what is retried, what is lost.
- **External writers**: other processes, agents, or users that touch the same state; who wins.
- **Compatibility**: existing data, callers, configs, and migrations.
- **Proof**: the test seam (prefer an existing one, as high as possible) and the end-to-end check.
- **Owen's own invariant**: take his words literally and try to break them.

## Write as you go

Create files lazily, only when there is something to write. Append settled answers as they land so a long session survives compaction.

- **Spec sheet**: the project's spec location if it has one, else `docs/specs/YYYY-MM-DD-<slug>.md` with `status: draft`. Use [spec-template.md](spec-template.md).
- **Glossary**: when a term resolves, update `GLOSSARY.md` at once, in [glossary-format.md](glossary-format.md). When Owen uses a term that conflicts with it, say so in the next round. No implementation detail in the glossary.
- **ADR**: offer one only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. Format and numbering in [adr-format.md](adr-format.md).

In a repo where Owen has no write rights or that is not his (for example an upstream he contributes to), ask before adding `GLOSSARY.md` or `docs/adr/`; the spec sheet can go in `.scratch/` with `.scratch/` added to `.git/info/exclude`.

## Closing

The grill is done only when all are true:

1. **The frontier is empty.** Every branch visited, nothing silently assumed, no hedge ("probably", "should be fine") left in an answer.
2. **Every invariant Owen asked for is provably unbreakable**, or you know where it breaks and he chose that.
3. **The restatement survives.** Read the spec back as numbered behavior statements grouped by surface, in the project's vocabulary, plus out of scope, touch points, and the end-to-end check. Any correction means you were not done: absorb it, restate only the changed statements, loop.
4. **Your own calls are listed.** Routine judgment calls you made instead of asking (naming, ordering, exact affordances) go under a heading Owen can skim and veto.
5. **Owen confirms.** Then set `status: agreed` in the spec sheet. If he says to stop asking, decide the open items yourself and list them under step 4.

Then hand off. Get explicit go-ahead before implementing unless already authorized. Prefer a fresh context that reads only the spec sheet; inside plan-then-ship, write these statements into its `SPEC.md` instead of a second file. Report implementation against the spec's numbered statements so Owen can check coverage without reading the diff. Do not commit the spec sheet, glossary, or ADRs unless the work is being committed.

## Gotchas

None recorded yet. Add one here when a run fails a new way.
