---
name: adversarial-review
description: Red-teams a code change by fanning out several independent reviewers with distinct assigned lenses, each required to produce a concrete failure scenario, then fixing and running a verifier pass whose job is to break the fix. Use when the user says "adversarial code review", "red-team this diff", "try to break this change", "review this hard", "use adversarial review to check the work", or asks for multiple independent reviewers on a change.
---

# Adversarial Review

Several reviewers attack one diff from different angles at the same time, none of them trusting the author. Findings that survive get fixed. Then a fresh reviewer attacks the fix.

Use it on any change worth being sure about — your own, a subagent's, a collaborator's. It does not need a spec and does not need the `plan-then-ship` pipeline.

**Related, do not confuse:** `plan-then-ship` owns the full plan → implement → ship pipeline, and its `review.md` is a sequential review scored against a written spec. This skill is the standalone, spec-free, parallel version. `plan-then-ship` may call into this skill for its review step; this skill never invokes that pipeline.

Read `lenses.md` before spawning anyone — it holds the lens catalog and the reviewer prompt template.

## The Principle

**A reviewer with no assigned lens re-finds what the last reviewer found.** Parallelism only buys coverage if each reviewer is looking somewhere different. Assign the lenses explicitly; never spawn N copies of "review this."

**A fix round is not the end.** In practice the first fix replaces a bad rule but keeps the bad *trigger* — the verifier round is what catches that. Budget for it from the start.

## Steps

### 1. Scope the change

Establish exactly what is under review and say so in every prompt: uncommitted working tree (`git diff` + `git status` for untracked files — do not forget untracked), a branch vs its base, or a PR number.

Write down what is **out of scope**: pre-existing bugs, unrelated files, known-and-accepted debt. Without this, reviewers spend their budget on real-but-irrelevant findings and you spend yours triaging them.

### 2. Pick 2–4 lenses

From `lenses.md`. Three is the usual number. Each reviewer gets exactly one lens and does not know the others exist.

Choose by what this change could plausibly break, not by a fixed checklist. A change touching persisted state always gets the data-loss lens. A change touching keybindings or UI always gets the interaction lens.

### 3. Fan out

If the harness can spawn parallel subagents, launch them in one batch so they run concurrently — a mid-tier model at high reasoning effort is right for this; the lens is doing the work, not raw model strength. If it cannot, run the lenses sequentially yourself in separate passes, resetting your framing between them.

Build each prompt from the template in `lenses.md`. Every prompt must carry:

- **"You are an adversarial reviewer. Your job is to break this, not to praise it."**
- **"Do not trust the author's summary."** Prose claims like "this falls out for free" are exactly what needs checking in code.
- The scope, the out-of-scope list, and the one lens.
- **The concrete-failure-scenario bar** (step 4).
- **"Do not edit any repo files."** Parallel reviewers writing to one tree corrupt each other's reads. Give them a scratch directory instead.
- Permission to run the test suite and to write throwaway tests in scratch.

### 4. Hold findings to the failure-scenario bar

Every finding must state: **exact starting state → exact action → exact wrong result.** A finding that cannot be written that way is discarded, not reported. Say this in the prompt; it is what keeps the report free of speculation.

### 5. Triage

- **Convergence is signal.** Two reviewers reaching the same defect down different paths means fix it first, before anything either found alone.
- **Root-cause, don't symptom-patch.** Several distinct-looking findings often share one cause; fix the cause once.
- **Discard the unreproducible**, no matter how plausible it sounds.
- **Out-of-scope but real** → file it separately (an issue, a spawned task). Do not fold it into this fix and do not silently drop it.

### 6. Fix

One fixer, given the findings, the intended new behavior stated as a rule, and an explicit "do not touch \<the out-of-scope items\>". Specify the desired contract in one sentence — if you only hand over the findings, the fixer invents a rule and it will be nearly-right.

Require new tests that **fail before the fix**, and require the fixer to confirm they did by reverting and running.

### 7. Verify — the round people skip

Spawn a **fresh** reviewer, not the fixer, told to disprove the fix. Give it the claimed contract verbatim and a numbered list of properties to prove or disprove.

It must:
- Test against the **real exported code path**, not the helper in isolation and not a re-implementation of the reducer/handler.
- **Flag any test that would still pass if the fix were reverted** — the sharpest finding available, and the one that catches a hollow fix.
- Re-check that the fix did not break something adjacent, and that renames left no stale references, comments, or docs.

If it finds something real, go back to step 6. Two fix→verify rounds is normal; more than three means the contract itself is wrong — stop and re-decide the design with the user rather than looping.

### 8. Verify it yourself, then report

Run the tests and typecheck **in your own shell**. A pasted result from a subagent is a claim, not evidence.

Report: what each lens found, what converged, what was fixed, what was discarded and why, what was filed as out-of-scope, and the real command output.

## Rules

- **One lens per reviewer.** Unlensed parallel reviewers are redundant reviewers.
- **Reviewers never edit the tree.** Read-only, scratch directory for experiments.
- **Never skip the verify round** because the fix looked clean. That round is where this skill earns its cost.
- **The author's summary is a hypothesis.** Including your own, when you were the author.
- **Name what is out of scope up front**, or you will triage noise.
- **Convergent findings first.** Independent paths to one defect is the strongest signal you get.
- **A test that passes against the unfixed code proves nothing.** Demand the fail-first confirmation.
- **Discard speculation.** No failure scenario, no finding.
- **Don't ship on a subagent's pasted green tests.** Re-run them.

## Failure modes

- Spawned three reviewers with the same generic prompt; got three copies of the same finding and missed everything else.
- Fix round replaced a broken *rule* but left the trigger keyed off the wrong thing (action type rather than actual effect), so the same class of bug survived. Only the verify round caught it.
- Verifier tested the extracted pure helper, which was correct, while the bug lived in how the caller invoked it.
- New test was written after the fix and never run against the unfixed code, so nobody noticed it passed either way.
- Reviewer reported a real pre-existing bug; it got folded into the fix, blew up the diff, and buried the actual change.
- Accepted "tests pass" from the fixer's report; the suite had not been run from the right directory.
- Reviewers all edited the same working tree in parallel and read each other's half-finished changes.
- Looped fix→verify four times because the contract was wrong; should have stopped at two and re-decided the design.
