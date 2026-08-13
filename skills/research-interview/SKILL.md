---
name: research-interview
description: Interview the user relentlessly, one question at a time, until the research question, hypotheses, constraints, and success criteria are pinned down with no ambiguity left — then write a research brief that /research-loop takes as grounding context. Use before starting a research-loop session, or when the user says "interview me about this project", "let's get on the same page before we research", "build a research brief", or hands you a vague research idea that isn't ready to run.
---

# Research Interview

Reach complete shared understanding of a research effort **before** any compute is spent — by interrogating, not assuming. The output is a brief that `/research-loop` reads at its **ground** step, so the loop starts from an agreed contract instead of a vibe.

**Position in the pipeline:** `research-interview` → `/research-loop` (→ `rosie-run` if the cluster is involved). If the user invokes `/research-loop` and no current brief exists, that's the cue to run this first.

## The Standard

The interview is done only when *both* of these are true, and not before:

1. **You can state the whole plan back and the user changes nothing.** Restate the research question, hypotheses, method, constraints, and success criteria in your own words. Any correction means you weren't done — absorb it and restate again. Loop until the restatement survives untouched.
2. **No load-bearing word is undefined.** "Better", "works", "fast enough", "the model", "the baseline" — every one gets pinned to a number, a name, or a path. If a term in the brief could mean two things, ask which.

Relentless means persistent, not rapid-fire. Keep going past the point of social comfort; do not keep going past the point of usefulness — when an answer is genuinely "we'll learn that from round 1", record it as an explicit open question with a plan to close it, and move on.

## The Rules That Make It Work

**One question per message. Never batch.** A list of six questions gets six shallow answers. Keep the preamble short too.

**Use the structured question tool when the harness has one.** In Claude Code, ask through `AskUserQuestion` — one question per call, with 2–4 concrete options when the answer space is genuinely enumerable (which partition, which baseline, which metric) so the user can tap instead of type; the built-in "Other" covers everything else. Fall back to plain chat for open-ended threads ("what would make you abandon this idea?") where options would anchor the answer. Never use the tool to batch several questions into one call — that's the same six-shallow-answers failure with buttons.

**Never ask what you can read.** Before the first question, read the project's `CONTEXT.md`/`README`, prior run logs, the relevant vault project note (`02-Projects/`), and any earlier briefs. Open by *presenting what you already believe* — question, method, constraints as you understand them — and ask what's wrong with it.

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
- **Resources** — data (paths, sizes, licenses), code state, hardware (which partition, how many GPUs, job-length limits).
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

Restate the whole plan. Incorporate corrections. Repeat until a restatement passes with zero changes. Only then mark the brief `status: agreed`.

### 5. Leave the artifact where /research-loop will look

Write the brief to **`research/briefs/YYYY-MM-DD-<slug>.md`** in the repo where `/research-loop` will run (create the directory if needed). If the effort has a vault project note in `02-Projects/`, add a one-line pointer to the brief there — the repo copy is the source of truth, the vault gets the pointer.

## The Brief Format

```markdown
---
status: agreed            # draft | agreed — /research-loop should refuse a draft
date: YYYY-MM-DD
project: <name>
---

# Research Brief — <title>

## Question
One falsifiable sentence, plus the result that would kill the idea.

## Hypotheses
Numbered; each with the evidence that would confirm or refute it.

## Success Criteria (objectives)
Metric, dataset, target number, and how it's measured.

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

## Interview Log
Date, participants, and the decisions that changed during the interview
(so future-you can see what was contentious).
```

## Rules

- **Never mark `status: agreed` without a clean pass of the closing loop.** A brief the user hasn't confirmed verbatim is a draft.
- **Record hedges as hedges.** "I think the license allows it" goes in Open Questions, not Resources.
- **Don't design the experiment for them.** Propose and challenge, but the hypotheses and priorities are the user's; your job is to make their intent unambiguous, not to substitute your own.
- **"Skip" is a valid answer** — but it becomes an explicit Open Question, never a silent gap.
- **State a number once.** Flag a budget overrun precisely, record it, move on; repeating it buries everything else.
- **One brief per effort.** A materially changed question gets a new dated brief, with the old one left in place — briefs are a record, not a wiki page.

## Environment

- zsh aborts on non-matching globs — use `find | while read`, not `for f in dir/*.md`.
- `ls` is aliased to a git-aware tool that hangs in large or fresh repos. Use `/bin/ls`.
