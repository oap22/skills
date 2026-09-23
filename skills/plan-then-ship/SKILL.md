---
name: plan-then-ship
description: "Plan a code change in exhaustive detail with a strong model, hand the spec to a weaker model to implement, then adversarially review, test, and ship. Use only when explicitly invoked: \"pipeline this\", \"plan then ship\", \"strong plan weak impl\". Not for ordinary coding or research."
---

# Plan Then Ship

A strong model writes a contract. A weaker model executes it. An adversarial review plus real tests gate the ship. Owen approves the spec. After that, same-tree or cloud implementers are both valid, and a repo with collaborators ships through a PR rather than by pretending they are not there.

This is **not** the default coding path. If he did not say one of the trigger phrases, do not run this skill.

**Read `models.md` before spawning anyone** — it explains how to select from the current capabilities.
**Read `interview.md` before asking Owen anything.** The spec is written *from* the interview, not instead of it.
**Read `spec-template.md` before writing the spec.**
**Read `review.md` before the first review pass.**
**Read `ship.md` before creating a branch or running any git write.**

## The Principle

The handoff is a **written spec**, not a chat summary. The weak model is not asked to design. With delegation available, the parent orchestrates and preserves one implementation owner.

A skill cannot swap the parent model mid-session. Use the capabilities and fallback rules in `models.md`; pass the full spec text to any implementer so an isolated checkout has the same contract.

## Roles

Three roles. Model selection and fallback rules live in `models.md`.

| Role | Job |
|---|---|
| **Planner** | Read the repo. Write the spec. Stop for approval. |
| **Implementer** | Execute the spec. No scope expansion. No "improvements." |
| **Reviewer** | Attack the diff against the spec, hunt edge cases, **run** the tests. |

## Steps

### 1. Choose roles

Per `models.md`. No historical model-name deny-list determines whether the current session may plan.

### 2. Interview and draft the spec

Per `interview.md`, drafting `.plan-then-ship/SPEC.md` from `spec-template.md`. Keep `.plan-then-ship/` ignored and out of commits.

### 3. Present the plan

Per `interview.md` (approval section). Do not begin dependent implementation while a required answer is pending.

### 4. Branch, then hand off

Follow `ship.md` § Branch **before** spawning. Implementation on `main`/`master` is a ship failure waiting to happen.

Pass the spec **path**, the **full spec text**, the feature-branch name, and this contract (cloud agents never see the gitignored file):

> Implement this spec exactly. A copy lives at `.plan-then-ship/SPEC.md` in a same-tree checkout; if you cannot read that path, the spec is the rest of this prompt. Do not expand scope. Do not improve the design. Do not touch files the spec marks do-not-touch. Work on feature branch `<branch>` off the repo default branch, never `main`/`master`. Run the test commands in the spec and report the actual output, redacting secrets. If the spec is contradictory or incomplete, stop and say so — do not invent a design.

**If the harness can spawn an agent with a named model:** spawn the implementer from `models.md` with that prompt. Same-tree is preferred. Cloud/isolated is allowed — see `models.md`. The parent does not write the code. After a cloud/isolated run, fetch that feature branch into this repo before review.

**If it cannot spawn:** follow the local sequential fallback in `models.md`, unless the user specifically required a separate-model handoff.

### 5. Adversarial review

After the implementer returns, the **planner/reviewer** role reviews. Read `review.md` and follow it. Cursor's dedicated review agents (bugbot, security-review) run *in addition* when they exist, not instead of running the spec's tests.

"Should pass" is not evidence. Run the relevant checks and report their outcomes, retaining useful output and redacting secrets per `review.md`.

### 6. Repair loop

Keep going until there are no criticals and tests are green. Suggestions never block and never start another loop.

Send criticals back to the implementer (same handoff rules as step 4). Re-review.

**Repair within the agreed budget.** Track whether the concrete defect is resolving; counts alone can hide progress when one root cause exposes another.

Stop when the loop cap or a stuck rule in `review.md` § Stuck rules fires (no progress, same finding, oscillation, spec is the problem). Looping the weak model cannot fix a bad contract — escalate to Owen.

**Escalate within budget.** When a stuck rule fires — or when Owen tests the live artifact and reports a defect still present after repairs, even with green tests (tests cannot see pixels) — the cheap implementer has hit its ceiling. Do not stop cold and do not spend another cheap pass on the same defect. Run **one escalation pass**: re-spawn the implementer on the **planner-tier model** from `models.md`, at an available reasoning effort appropriate to the remaining investigation and budget, scoped to only the surviving defects, with an investigation mandate — question the standing diagnosis rather than iterating on it, research known issues in the involved libraries/platforms, and full license to re-architect the failing component within the spec's boundaries. Do this only when a coherent spec and the remaining authorized budget support another pass. If the escalation pass also fails, stop and report per the rules above.

On any stop: report the remaining criticals, which stuck rule fired, whether the escalation pass ran, and that the diff is unshipped. Do not silently lower the bar to "close enough."

### 7. Ship

Review clean and tests green. Then follow `ship.md` in full: permission check, named-files commit (or reuse the cloud agent's commit), push the **feature branch** to `origin`, open the PR, request CODEOWNERS/collaborator reviewers when they exist, merge only if you have merge rights and CI is actually green. Waiting is not passing. A required-review block is success of the multi-person path — leave the PR up.

## Rules

- **Do not run this unless it was invoked.** Ordinary "add a feature" is not this skill.
- **Resolve consequential unknowns; decide routine details.** The spec records both so the implementer does not need to guess.
- **Honor explicit approval of the concrete plan.** Do not ask again for an already authorized step.
- **Use one implementation owner.** The parent may implement in the documented no-delegation fallback, but never compete with an active implementer.
- **The spec is the only source of truth for the implementer.** Conversation context is not a substitute. If it is not in the spec, it does not happen.
- **Keep actual test evidence.** Summarize commands and outcomes in the report, retain logs when useful, and redact secrets. Raw output does not need to flood the conversation.
- **Suggestions are not criticals.** Promoting a nit to a blocker to keep looping is how this skill burns money.
- **A bad spec escalates; it does not loop.** The human gate already happened. If the contract is wrong, Owen rewrites it.
- **Not for research.** `research-loop` owns experiments. This skill ships product/tooling code.
- **Not a replacement for Cursor Plan mode** — Plan mode can be step 2. The spec file is still the handoff.
- **Follow the actual default-branch policy; do not directly push the default branch.** Feature branch, then PR. `ship.md` is the procedure.
- **The spec travels in the prompt.** Path-only handoff fails for cloud and worktree agents. Always include the full text.
- **Collaborators are a workflow, not a stop.** Open the PR. Request reviewers. Merge only with merge rights; if GitHub requires a human review, that is the handoff.

## Failure modes

- Spec was a paragraph of intent. Weak model designed anyway. The planner failed, not the implementer.
- Planner wrote the spec straight from Owen's one-liner without interviewing; the thin spec left consequential behavior ambiguous until review instead of before the implementer ever ran. Routine file choices, by contrast, did not need a separate interview.
- Owen said "looks good" after the first section and the planner took that as full approval instead of finishing the closing loop.
- Parent "helped" by writing the hard files. Cost savings gone; review is now self-review.
- Reviewer skipped the test commands because the code "looked right."
- Repair loop treated new nits as criticals, so the finding set never shrank.
- Shipped with WRITE but not merge rights, because the push succeeded.
- Implemented on `main`, then `git push` updated the default branch before a PR existed.
- Merged after `gh pr checks --watch` returned because "wait" was treated as "pass."
- Spawned a cloud agent with only a spec path, so it never saw the contract.
- Pasted raw test logs containing tokens into chat.
