# Spec template

The planner writes this file to `.plan-then-ship/SPEC.md` in the **target repo**, not in the skills repo. Every section is required. If a section has nothing to say, write `None` and why — omitting it is how the implementer starts designing.

The implementer is forbidden to outthink this document. If a decision is not in here, it does not happen. The parent always pastes this whole file into the implementer prompt so a cloud or worktree agent can run without reading the gitignored path.

```markdown
# Spec

## Goal

One paragraph. What will be true when this is done.

## Non-goals

Bullet list. Explicitly out of scope. These prevent the implementer from "while I'm here."

## Files

### Touch

Exact paths, one per line. The implementer may only write these files (and test files listed under Tests). `.gitignore` is planner work, not a Touch path — see `ship.md`.

### Do not touch

Exact paths or glob patterns. Touching one is a critical finding.

## Per-file edits

One subsection per path in Touch. For each:

- **What changes.** Function/type/export names. New signatures in full, not "add a helper."
- **Control flow.** What happens on the happy path, in order.
- **Edge cases.** Empty input, missing file, already-exists, permission, timeout, the zero and the many.
- **Error paths.** What throws, what returns, what is swallowed. Nothing silent unless this spec says so.
- **What stays.** Adjacent code the implementer might be tempted to clean up. Leave it.

## Tests

- **Add or change.** Exact paths and what each test asserts.
- **Commands.** The precise shell commands to run, from the repo root, with any env that is required.
- **Passing looks like.** What stdout/exit code counts as green. "The tests pass" is not enough — name the suite and the expected summary line if the project has one.

## Commit and PR

- **Commit message.** 1–2 sentences, why not what. Ready to use as `git commit -m`.
- **PR title.**
- **PR body.** Summary bullets and a test plan copied from the commands above.

## Acceptance criteria

A checklist the reviewer will score against. Each item is observable (a file exists, a command exits 0, a behavior is absent). No "code is clean."

## Notes for the implementer

Anything that would otherwise leak from the planning conversation: a library already in the repo to prefer, a pattern to copy from a named file, a pitfall already discovered. Still not a license to invent.
```

## Bar for "excruciating"

A spec that a cheaper model can execute without asking a question. If you would need to be in the room to explain a sentence, rewrite the sentence.

Fail this bar:

- "Refactor the auth layer for clarity."
- "Handle errors properly."
- "Add tests as appropriate."
- "Follow existing patterns." (Name the file and the function to copy.)

Pass this bar:

- "In `src/auth/session.ts`, replace `validateSession` (currently L40–58) with a check that returns `null` when `token` is missing or `exp` is in the past, *then* looks up the row. Do not keep the empty-token fallback. Add `session.test.ts` covering missing token, expired token, and a valid row. Command: `npm test -- session.test.ts`."

## After Owen approves

Do not keep editing the spec unless he asked. The approved file on disk is the contract. A silent tweak after approval is a different spec he did not see.
