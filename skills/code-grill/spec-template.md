# Spec Sheet Template

Path: the project's spec location if it has one, else `docs/specs/YYYY-MM-DD-<slug>.md`. Use the glossary's terms throughout and respect ADRs in the area. Fill sections as answers settle; delete a section only when it truly does not apply, and say so in Further notes.

Adapted from `to-spec` in https://github.com/mattpocock/skills (MIT, Copyright (c) 2026 Matt Pocock).

```md
---
status: draft            # draft | agreed | implemented | superseded by <path>
date: YYYY-MM-DD
repo: <repo name>
---

# <Change title>

## Problem

The problem from the user's or caller's point of view.

## Solution

The solution from the user's or caller's point of view, in two to five sentences.

## Behavior

Numbered statements, grouped by surface (screen, command, endpoint, module). Each is testable and uses glossary terms. Implementation is checked against these numbers.

### <Surface>

1. When <condition>, <actor> sees / gets <result>.
2. ...

## User stories

A long numbered list covering every actor and path, including errors and edge cases.

1. As a <actor>, I want <capability>, so that <benefit>.

## Decisions

- Modules built or changed, and their interfaces.
- Data and schema changes; migrations.
- API or CLI contracts.
- Architectural decisions, with links to ADRs (`docs/adr/NNNN-slug.md`).
- A snippet only when it encodes a decision more precisely than prose (state machine, schema, type shape); trim to the decision.

## Touch points (as of <date>)

Files, symbols, and interfaces the change is expected to touch. These drift; the Behavior and Decisions sections are the contract.

## Testing

- What a good test checks here (external behavior, not internals).
- The seam(s) agreed with Owen, and prior-art tests to copy.
- **End-to-end check**: the one real run that proves the behavior on the target.

## Out of scope

Things raised and deliberately excluded, with a one-line reason each.

## Calls made without asking

Routine judgment calls (naming, ordering, exact affordances) for Owen to skim and veto.

## Further notes

Open risks, follow-ups, and anything that did not fit above.
```
