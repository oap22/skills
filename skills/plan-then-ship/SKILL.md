---
name: plan-then-ship
description: Plans a code change in exhaustive detail with a strong model, hands the spec to a weaker model to implement, then adversarially reviews, tests, and ships. Use when the user says "pipeline this", "plan then implement", "strong plan weak impl", or "plan then ship". Not for ordinary coding, research experiments, or work that was not explicitly invoked this way.
---

# Plan Then Ship

A strong model writes a contract. A weaker model executes it. An adversarial review plus real tests gate the ship. Owen approves the spec. After that, same-tree or cloud implementers are both valid, and a repo with collaborators ships through a PR rather than by pretending they are not there.

This is **not** the default coding path. If he did not say one of the trigger phrases, do not run this skill.

**Read `models.md` before spawning anyone** — that is the role → model mapping, and it goes stale.
**Read `interview.md` before asking Owen anything.** The spec is written *from* the interview, not instead of it.
**Read `spec-template.md` before writing the spec.**
**Read `review.md` before the first review pass.**
**Read `ship.md` before creating a branch or running any git write.**

## The Principle

The handoff is a **written spec**, not a chat summary. The weak model is not asked to design. The parent orchestrates; it does not re-implement.

A skill cannot swap the parent model mid-session. If the harness can spawn an agent with a named model, do that. Always put the **full spec text** in the prompt, not only a path — cloud and worktree agents cannot read a gitignored local file. Prefer same-tree spawn when it exists; cloud/isolated spawn is a first-class path, not a fallback to avoid. Only if no named-model spawn exists at all: stop and tell Owen which model to switch to and the exact next sentence to send.

## Roles

Three roles. Names of models live in `models.md`, not here.

| Role | Job |
|---|---|
| **Planner** | Read the repo. Write the spec. Stop for approval. |
| **Implementer** | Execute the spec. No scope expansion. No "improvements." |
| **Reviewer** | Attack the diff against the spec, hunt edge cases, **run** the tests. |

If this session is already the implementer model, **do not plan**. Say so and ask to restart on the planner model.

## Steps

### 1. Confirm you are the planner

Read `models.md`. If the current model is the implementer for this harness, stop. Otherwise continue as planner.

### 2. Interview, then write the spec

Read the repo until the change is concrete. Then follow `interview.md`: one question at a time, load-bearing unknowns first, drafting `.plan-then-ship/SPEC.md` from `spec-template.md` as answers land — not after. Every field is required. A vague spec is how the weak model starts designing, which is the failure this skill exists to prevent, and a vague spec is what you get if you skip straight to writing instead of interviewing.

A one-line request from Owen is the opening move of the interview, not a spec-ready brief. Do not fill a section from your own guess when a single question would replace the guess with a fact.

Ensure `.plan-then-ship/` is in the repo's `.gitignore`. Do not commit the spec.

Cursor Plan mode can *be* this step. The spec file is still required — it is what the rest of the pipeline reads. The interview obligation applies inside Plan mode too; a Plan-mode session that infers instead of asking has the same failure mode.

### 3. Closing loop, then gate — stop for approval

Before showing Owen anything, run the closing loop from `interview.md` § 4: restate the whole spec back to him, section by section, in your own words. Incorporate corrections, restate again. Repeat until one full pass changes nothing — an "ok looks good" that interrupts an unfinished loop does not count, keep restating.

Only once the loop closes clean does the human gate open. Show Owen the spec file on disk. Do not spawn the implementer, do not edit code, do not "start on the easy files while he reads." Wait.

If he changes the spec, rewrite it and run the closing loop again before re-presenting. Approval is of a file he has heard read back to him and confirmed unchanged, not of a vibe.

### 4. Branch, then hand off

Follow `ship.md` § Branch **before** spawning. Implementation on `main`/`master` is a ship failure waiting to happen.

Pass the spec **path**, the **full spec text**, the feature-branch name, and this contract (cloud agents never see the gitignored file):

> Implement this spec exactly. A copy lives at `.plan-then-ship/SPEC.md` in a same-tree checkout; if you cannot read that path, the spec is the rest of this prompt. Do not expand scope. Do not improve the design. Do not touch files the spec marks do-not-touch. Work on feature branch `<branch>` off the repo default branch, never `main`/`master`. Run the test commands in the spec and report the actual output, redacting secrets. If the spec is contradictory or incomplete, stop and say so — do not invent a design.

**If the harness can spawn an agent with a named model:** spawn the implementer from `models.md` with that prompt. Same-tree is preferred. Cloud/isolated is allowed — see `models.md` § Spawn. The parent does not write the code. After a cloud/isolated run, fetch that feature branch into this repo before review.

**If it cannot spawn at all:** stop and tell Owen to switch to the implementer model and send the paragraph above (with spec text attached) verbatim.

### 5. Adversarial review

After the implementer returns, the **planner/reviewer** role reviews. Read `review.md` and follow it. Cursor's dedicated review agents (bugbot, security-review) run *in addition* when they exist, not instead of running the spec's tests.

"Should pass" is a fail. Paste the real command and the real stdout, with secrets redacted per `review.md`.

### 6. Repair loop

Keep going until there are no criticals and tests are green. Suggestions never block and never start another loop.

Send criticals back to the implementer (same handoff rules as step 4). Re-review.

**Default is keep repairing.** Stop only when stuck, not because it is taking a while.

Hard stop at **4 repair loops**: review pass 1 is the initial review; each repair is followed by another review; after repair 4 comes review pass 5. If pass 5 still has criticals or red tests, stop. Do not start a fifth repair. Also stop *earlier* if any of these fire:

- **No progress.** Critical count did not strictly decrease this round.
- **Same finding, unchanged.** A critical at the same location with the same claim survived a repair.
- **Oscillation.** Round N reintroduces a critical that round N-1 had closed.
- **Spec is the problem.** Implementer or reviewer can show the spec is contradictory, incomplete, or wrong. Looping the weak model cannot fix a bad contract — escalate to Owen.

**Escalate before stopping.** When a stuck rule fires — or when Owen tests the live artifact and reports a defect still present after repairs, even with green tests (tests cannot see pixels) — the cheap implementer has hit its ceiling. Do not stop cold and do not spend another cheap pass on the same defect. Run **one escalation pass**: re-spawn the implementer on the **planner-tier model** from `models.md`, at the highest reasoning effort the harness offers, scoped to only the surviving defects, with an investigation mandate — question the standing diagnosis rather than iterating on it, research known issues in the involved libraries/platforms, and full license to re-architect the failing component within the spec's boundaries. This is the one sanctioned inversion of "never use the planner tier to implement," and Owen saying "it's still broken" after a repair pass is an automatic trigger. If the escalation pass also fails, stop and report per the rules above.

On any stop: report the remaining criticals, which stuck rule fired, whether the escalation pass ran, and that the diff is unshipped. Do not silently lower the bar to "close enough."

### 7. Ship

Review clean and tests green. Then follow `ship.md` in full: permission check, named-files commit (or reuse the cloud agent's commit), push the **feature branch** to `origin`, open the PR, request CODEOWNERS/collaborator reviewers when they exist, merge only if you have merge rights and CI is actually green. Waiting is not passing. A required-review block is success of the multi-person path — leave the PR up.

## Rules

- **Do not run this unless it was invoked.** Ordinary "add a feature" is not this skill.
- **No spec section from inference when a question would replace the guess.** The interview exists so the implementer never has to guess either. See `interview.md`.
- **The closing loop isn't optional because Owen seems fine with it.** Restate until a full pass survives untouched; an early "sounds good" doesn't skip the rest of the sections.
- **The parent does not implement.** If you catch yourself editing the code the implementer was supposed to write, you have broken the pipeline.
- **The spec is the only source of truth for the implementer.** Conversation context is not a substitute. If it is not in the spec, it does not happen.
- **Tests were not run if the output is not pasted.** Same floor as `research-loop`. Redact secrets in the paste; do not skip the paste.
- **Suggestions are not criticals.** Promoting a nit to a blocker to keep looping is how this skill burns money.
- **A bad spec escalates; it does not loop.** The human gate already happened. If the contract is wrong, Owen rewrites it.
- **Not for research.** `research-loop` owns experiments. This skill ships product/tooling code.
- **Not a replacement for Cursor Plan mode** — Plan mode can be step 2. The spec file is still the handoff.
- **Never commit or push `main`/`master`.** Feature branch, then PR. `ship.md` is the procedure.
- **The spec travels in the prompt.** Path-only handoff fails for cloud and worktree agents. Always include the full text.
- **Collaborators are a workflow, not a stop.** Open the PR. Request reviewers. Merge only with merge rights; if GitHub requires a human review, that is the handoff.

## Failure modes

- Spec was a paragraph of intent. Weak model designed anyway. The planner failed, not the implementer.
- Planner wrote the spec straight from Owen's one-liner without interviewing, then discovered the ambiguity at review instead of before the implementer ever ran.
- Owen said "looks good" after the first section and the planner took that as full approval instead of finishing the closing loop.
- Parent "helped" by writing the hard files. Cost savings gone; review is now self-review.
- Reviewer skipped the test commands because the code "looked right."
- Repair loop treated new nits as criticals, so the finding set never shrank.
- Shipped with WRITE but not merge rights, because the push succeeded.
- Session was already the cheap model and it wrote a thin spec rather than refusing.
- Implemented on `main`, then `git push` updated the default branch before a PR existed.
- Merged after `gh pr checks --watch` returned because "wait" was treated as "pass."
- Spawned a cloud agent with only a spec path, so it never saw the contract.
- Pasted raw test logs containing tokens into chat.
