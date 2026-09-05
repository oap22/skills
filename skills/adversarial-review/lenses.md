# Lenses and the reviewer prompt

## The lens catalog

Pick 2–4. Each goes to exactly one reviewer. The parenthetical is the question the lens actually asks.

| Lens | Hunts for | Always use it when |
|---|---|---|
| **Correctness & data loss** (*can this silently destroy something the user made?*) | Persistence and migration paths, state that survives restart, edge cases at boundaries, actions that fire when they shouldn't | The change touches persisted state, storage schemas, migrations, or anything a returning user has on disk |
| **Spec conformance & completeness** (*did it do what was asked, everywhere?*) | Missed call sites, stale comments and docs, dead code, leftovers from a rename, half-applied changes | Any change that replaces a constant, widens a range, or renames something |
| **Interaction & UX** (*will this feel broken?*) | Keybinding conflicts, surprising state changes, silent no-ops, discoverability, things vanishing without user action | The change touches keybindings, UI affordances, or anything the user drives directly |
| **Test honesty** (*would these tests pass if the change were reverted?*) | Tautological assertions, tests weakened to fit new behavior, untested branches, mocked-away subjects | The author changed existing tests rather than only adding new ones |
| **Concurrency & lifecycle** (*what happens when two of these race?*) | Re-entrancy, effects firing mid-render, cleanup, ordering assumptions, double-invocation | The change touches effects, subscriptions, async orchestration, or shared mutable state |
| **Security** (*what does an attacker do with this?*) | Injection, authz gaps, secrets in logs or URLs, trust of external input | The change touches auth, user input, network boundaries, or file paths |
| **Blast radius** (*what else reads this?*) | Downstream consumers, public API shape, callers outside the changed package, docs and READMEs elsewhere in the repo | The change alters an exported signature, a constant, or a data format |

**Test honesty is worth its own reviewer** whenever the author edited existing tests. Folding it into another lens gets it done shallowly — it is the lens most likely to find that a fix is hollow.

## Reviewer prompt template

Fill the bracketed parts. Keep every unbracketed sentence — each one is load-bearing.

> Think hard. You are an ADVERSARIAL code reviewer. Your job is to BREAK this change, not to praise it. Assume it is wrong until you have proven otherwise by reading the code. Do not trust the author's summary — prose claims are exactly what needs checking against the code.
>
> Repo: `[absolute path]`
> See the change with: `git -C <repo> diff` and `git -C <repo> status` (do not miss untracked files).
>
> ## Context: what was asked for
> [The intended behavior, stated as a contract. Include agreed design decisions so the reviewer can tell "wrong" from "deliberate".]
>
> ## Your lens: [LENS NAME]
> [3–6 numbered, specific things to hunt for, phrased as questions to answer by reading code. Name the exact files and functions where you suspect trouble — a lens plus a pointer beats a lens alone.]
>
> ## Out of scope
> [Pre-existing bugs, unrelated files, accepted debt. Be explicit; anything not listed will get reported.]
>
> ## The bar
> For every candidate finding, WRITE THE CONCRETE FAILURE SCENARIO: exact starting state, exact action, exact wrong result. If you cannot construct one, DISCARD the finding — do not report speculation.
>
> Verify claims by reading code, and where cheap by running the test suite or writing a throwaway test under `[scratch dir]`. Test the REAL exported code path, not an isolated helper and not your own re-implementation.
>
> Do NOT edit any repo files (scratch files are fine). Report findings only, ranked most severe first, each with file:line, the failure scenario, and a suggested fix. If you find nothing real in your lens, say so plainly — a clean report is a valid result, but only after you have genuinely tried to break it.

## Verifier prompt template

For step 7. Different in kind from a lens reviewer: it gets the claimed contract and a list of properties.

> Think hard. You are an ADVERSARIAL verifier. A previous agent claimed to fix review findings. Your job is to prove the fixes are WRONG or INCOMPLETE. Do not trust the claim.
>
> Repo: `[path]`. Read `git -C <repo> diff` in full first.
>
> ## The claimed contract
> [Verbatim, one sentence if possible.]
>
> ## Prove or disprove each of these by reading the code, and where useful by writing throwaway tests under `[scratch dir]` and running them:
> [Numbered properties. Include at least one that should hold, one that should NOT hold, and one about a path the fixer said "falls out for free" — prose claims that are true in English and false in code are the common failure.]
>
> Also:
> - Test against the REAL exported code path, not a helper in isolation and not a re-implementation.
> - Read the new and changed tests. **Flag any test that would still pass if the fix were reverted** — that is the sharpest possible finding.
> - Check the fix broke nothing adjacent, and that any rename left no stale reference, comment, or doc.
>
> Do NOT edit repo files (scratch is fine). Rank findings most severe first with file:line and a repro. If the fixes hold up, say so plainly — but only after actually trying to break them, and list what you tested.

## Fixer prompt notes

Not a review prompt, but it fails in a predictable way: handing over findings alone makes the fixer invent a rule, and the invented rule is nearly-right.

Always include:
- **The new contract as one explicit sentence**, not just the list of defects.
- Which findings are in scope and which are deliberately not.
- Where the new logic belongs, if the review revealed the old code put it in the wrong layer.
- "Add tests that FAIL before this fix. Confirm the pre-fix failure in a disposable worktree or scratch copy, and report the evidence. Never revert or stash shared work."
- "Report the exact commands you ran and their real output. If something fails and you cannot fix it, say so plainly rather than claiming success."
