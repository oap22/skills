---
name: research-interview
description: "Clarify a research effort through a one-question-at-a-time interview and write a research brief. Use for \"build a research brief\" or \"interview me about this research\". Also for pinning down a research question, hypotheses, success criteria, or budget before compute is spent. Not for running the experiment (research-loop), a web literature survey (research-survey), or a product feature spec (feature-interview); an agreed plan is reused, not re-interviewed."
---

# Research Interview

Reach complete shared understanding of a research effort **before** any compute is spent — by interrogating, not assuming. The output is the brief that `/research-loop`'s design gate (hypothesis, measurement, control, falsifier, confounds) is filled from, so the loop starts from an agreed contract instead of a vibe.

**Position in the pipeline:** `research-interview` → `/research-loop` (→ `rosie-run` if the cluster is involved). Before interviewing, check for prior agreement. An agreed brief in `research/briefs/` that covers this question: write nothing and hand off to `/research-loop`. A draft brief: resume from its Open Questions. Agreement only in the conversation or a handoff: write it as the brief with `status: agreed`, cite where it was agreed, and ask only about consequential gaps. Owen says skip: write what is known, put each gap in Open Questions, and mark agreed only if he approves the restated plan.

**When Owen says he will be watching the Turing desktop app**, also load the `turing` skill and record in the brief's Resources the run directory under its watched results root, so the execution phase renders live.

## The Standard

The interview is done only when *both* of these are true, and not before:

1. **You can state the whole plan back and the user changes nothing.** Restate the research question, hypotheses, method, constraints, and success criteria in your own words. A material correction means you weren't done — absorb it and restate again; explicit approval of the concrete plan ends the loop.
2. **No load-bearing word is undefined.** "Better", "works", "fast enough", "the model", "the baseline" — every one gets pinned to a number, a name, or a path. For an LLM or agent, "the model" means the exact version string, prompt file, and decoding settings, including any judge model. If a term in the brief could mean two things, ask which.

Be persistent, not rapid-fire. Keep going past the point of social comfort; do not keep going past the point of usefulness — when an answer is genuinely "we'll learn that from round 1", record it as an explicit open question with a plan to close it, and move on.

## The Rules That Make It Work

**One question per message. Never batch.** A list of six questions gets six shallow answers. Keep the preamble short too.

**Use the structured question tool when the harness has one.** Follow that tool's current usage rules — one question per call, with 2–4 concrete options when the answer space is genuinely enumerable (which partition, which baseline, which metric) so the user can tap instead of type; the built-in "Other" covers everything else. Fall back to plain chat for open-ended threads ("what would make you abandon this idea?") where options would anchor the answer. Never use the tool to batch several questions into one call — that's the same six-shallow-answers failure with buttons.

**Never ask what you can read.** Before the first question, read the project's `CONTEXT.md`/`README`, `research/JOURNAL.md`, `DEAD-ENDS.md`, `OPEN-QUESTIONS.md`, recent runs in the shared results root, the relevant vault project note (`02-Projects/`), and any earlier briefs. Open by *presenting what you already believe* — question, method, constraints as you understand them — and ask what's wrong with it.

**Follow the thread.** Each question comes from the last answer, not a checklist. A hedge ("probably", "I think", "should be fine") is a thread — pull it.

**Attack the design, don't just record it.** You are the first adversarial reviewer. If the baseline is weak, the metric gameable, the sample size hopeless, or the hypothesis unfalsifiable, say so during the interview — that's cheaper than discovering it after a run.

## Ground to Cover

As threads, not a script — but the brief cannot be written until each has either an answer or an explicit open question:

- **The question** — one sentence, falsifiable. What result would make the user abandon the idea?
- **Hypotheses** — what they believe now, and what evidence would move them.
- **Success criteria vs. gates** — the objective being maximized, separately from the constraints that must merely hold. Conflating these is the classic failure `/research-loop` guards against.
- **Baseline and noise floor** — what the result is compared against, and the seed-to-seed variance below which a delta means nothing. If no noise floor exists yet, measuring one is round 0.
- **Stopping criterion** — pre-committed: how many rounds, what saturation looks like, what triggers stop. `/research-loop` will refuse to be honest for you later if this is decided after seeing results.
- **Budget** — compute hours, dollars, wall-clock deadline, and human-attention load the user will tolerate.
- **Resources** — data (paths, sizes, licenses, and which split is held out until the final round), code state, hardware (which partition, how many GPUs, job-length limits).
- **Non-goals** — what this effort is explicitly not trying to answer. These prevent scope creep in later rounds.
- **Priors and dead ends** — what's been tried, what failed, and why. Failed attempts are the cheapest experiments available.

## Steps

### 1. Read first, then show your work

Read everything relevant, present the inferred picture, and ask what's wrong. Flag contradictions between sources — a project note that says 16 GPUs when the facts file says 8 is a real question.

### 2. Interview, one question at a time

Start with the most load-bearing unknown — usually the question itself or the success criterion. Do arithmetic on answers as they land (runs × hours × nodes vs. the stated budget) and surface the result immediately; "that sweep is 3× your budget" is worth more mid-interview than in the brief.

### 3. Write as you go

Draft the brief **during** the interview, not at the end. Long conversations get compressed; unwritten answers are lost answers. Keep an `## Open Questions` section and prune it as answers land.

### 4. Run the closing loop

Restate the whole plan and apply corrections per Standard 1; then mark the brief `status: agreed`.

### 5. Leave the artifact where /research-loop will look

Write the brief to **`research/briefs/YYYY-MM-DD-<slug>.md`** in the repo where `/research-loop` will run (create the directory if needed). If that repo does not exist yet, ask where the work will live; until then keep the draft in the vault project folder. If the effort has a vault project note in `02-Projects/`, add a one-line pointer to the brief there — the repo copy is the source of truth, the vault gets the pointer.

## The Brief Format

```markdown
---
status: agreed            # draft | agreed — do not start a run from a draft
date: YYYY-MM-DD
project: <name>
---

# Research Brief — <title>

## Question
One falsifiable sentence, plus the result that would kill the idea.

## Hypotheses
Numbered; each with the evidence that would confirm or refute it. Only these are confirmatory; report every one, nulls included.

## Success Criteria (objectives)
Metric, dataset, the smallest effect worth acting on, seeds per arm, and the decision rule (test or CI) that turns results into confirmed / refuted / inconclusive. Fixed now, not after round 1.

## Gates (constraints that must hold)
Distinct from objectives — e.g. human-gate load must not rise.

## Baseline & Noise Floor
What we compare against; measured seed variance, or "round 0 measures it".

## Stopping Criterion
Pre-committed rounds / saturation definition / abort triggers.

## Budget
Compute, money, wall-clock, human attention.

## Resources
Data paths, code state, hardware, partition and job limits.

## Non-Goals
What this effort will not answer.

## Priors & Dead Ends
What was tried, what failed, why.

## Open Questions
Each with the round or action that will close it. Empty is the goal;
honest is the requirement.

## Deviations
Appended after agreement, never edited: date, what changed from this brief, why, and whether results seen so far informed it. Anything added here is exploratory.

## Interview Log
Date, participants, and the decisions that changed during the interview
(so future-you can see what was contentious).
```

## Rules

- **Never mark `status: agreed` without a clean pass of the closing loop.** Explicit approval of the concrete plan suffices; do not require verbatim repetition or restart the interview after a minor correction.
- **Record hedges as hedges.** "I think the license allows it" goes in Open Questions, not Resources.
- **Don't design the experiment for them.** Propose and challenge, but the hypotheses and priorities are the user's; your job is to make their intent unambiguous, not to substitute your own.
- **"Skip" is a valid answer** — but it becomes an explicit Open Question, never a silent gap. A brief can be agreed with open questions only if each names the round that closes it and none is the Question or the Success Criteria.
- **State a number once.** Flag a budget overrun precisely, record it, move on; repeating it buries everything else.
- **One brief per effort.** A materially changed question gets a new dated brief, with the old one left in place — briefs are a record, not a wiki page.

## Gotchas

None recorded yet. Add one here when a run fails a new way.
