# Driving Functions — Self-Improving Loops

Read this whenever the work is a **loop that feeds its own output back into itself**: a self-improvement flywheel, an iterative refinement scheme, curriculum generation, agent-improves-agent, synthetic-data retraining, or any process where round *N+1* is built from round *N*'s output.

Ordinary experiments ask *did this change help?* Self-improving loops ask a harder question: **how far does this go, how fast, at what cost, and where does it stop?** Answering it needs machinery a single-run experiment doesn't.

## The Distinction That Reframes Everything

**A gate is not an objective.**

| | Gate | Objective (driving function) |
|---|---|---|
| Answers | "Ship this round?" | "How much better is round 3 than round 2?" |
| Type | Pass / fail | Scalar, comparable across rounds |
| Tells you when to stop | No | Yes |
| Example | held-out delta > 0 **and** diversity floor met | Δ held-out score per round, in units of seed noise |

A loop built entirely of gates runs forever and produces no curve. It will happily report "round 7 passed" while the actual gain per round went to zero at round 3. **Every self-improving loop needs at least one driving function, and the gates stay as constraints on top of it.** Building the gate first and calling it the objective is the most common way this work goes wrong.

## Requirements for a Driving Function

A driving function is only load-bearing if all four hold. Check them explicitly, in writing, at the design gate:

**1. Mechanically verifiable.** Ground truth comes from a checker, not a human judgment. If a person sits in the reward seat, the loop is rate-limited by that person, the signal drifts as they get tired or change their mind, and cross-round comparison is confounded by the drift. Tasks with checkable answers — math with a verifier, code with tests, predictions against held-out labels — are the price of admission to unattended operation, and unattended operation is the precondition for sweeping.

**2. Held out and uncontaminated.** The eval set must be genuinely unseen. For anything involving a pretrained model, public benchmarks have a contamination risk unless training provenance establishes otherwise. Prefer **programmatically generated problems with checkers**, or independently held-out items. Publication after a claimed cutoff alone does not prove isolation. Keep the final test set separate from repeated development evaluations.

**3. In the difficulty band.** Above the floor and below the ceiling. A metric where the system scores 0 every round measures nothing; so does one where it scores 100. Verify the band with a pilot before round 1 — this is cheap and catches a wasted sweep.

**4. Not the thing you actually care about, and you know it.** Optimizing for checkable answers improves checkable answers. Any claim beyond that needs a **secondary axis the loop cannot optimize against** — a small, held-out, differently-shaped measure, checked each round purely to detect the gap opening up. When the primary climbs and the secondary doesn't, you've found Goodhart's law, and that's a real result. Design the secondary axis *before* round 1 or you will not believe it later.

## The Four Numbers Every Loop Reports

The primary score alone is not enough to answer "how far does this go." Log all four, every round.

### 1. Primary score
Held-out performance on the verifiable task. The headline, and the least interesting on its own.

### 2. Marginal round gain — Δ score per round
The actual shape of the trajectory. **Saturation is when Δ drops below the seed-noise floor** — which means the noise floor must exist before Δ means anything. See § The Noise Floor Comes First.

### 3. Cost per unit gain
GPU-hours and dollars per point of improvement. This is the denominator in "how far can I push this," and it's what makes the work an engineering result rather than a curve. It usually degrades faster than the primary score improves; that crossover is often the real finding.

### 4. Human-gate load — interventions required per round
Count every decision a human had to make for the round to complete. **If this number rises, the loop is not self-improving — it is a treadmill with extra steps.** Trending to zero is not bookkeeping; for a self-improvement claim it is frequently the headline result, and it's the number most likely to go unmeasured because nobody thinks to count their own labor.

**Constraints ride alongside, not inside.** Diversity floors, tail coverage, and collapse detection stay as pass/fail gates. Do not fold them into the primary scalar as a weighted sum — a blended score hides which term moved, and "the number went up" stops meaning anything.

## The Noise Floor Comes First

**Before round 1, run the same configuration at ≥3 seeds and measure the spread.** That spread is the noise floor.

This is the single most skippable and least skippable step in the whole protocol. Without it:

- "Round 4 improved by 0.8 points" is an uninterpretable statement.
- Saturation cannot be defined, so the stopping criterion cannot exist.
- Every round-over-round comparison is vulnerable to the objection that you're reading noise, and the objection will be correct roughly as often as not.

The noise floor is itself a logged run. Put the number in the trajectory record and reference it in every subsequent round's entry.

**→ This is a Cost gate.** Seeds multiply compute. Bring the estimate.

## Stopping Criterion — Defined Before Round 1

Write the halting condition down before the loop starts, at the design gate. A loop without a pre-committed stopping rule runs until you get bored, and "I stopped at round 6" is then a fact about your patience, not about the system.

```markdown
**Stop when any of:**
- Marginal gain < noise floor for N consecutive rounds   (saturation)
- A constraint gate fails                                 (collapse / diversity floor breached)
- Cost per unit gain exceeds <threshold>                  (no longer worth it)
- Secondary axis diverges from primary by <margin>        (Goodhart — the loop is gaming the metric)
- Round budget R reached                                  (hard backstop, always set one)
```

**Measure saturation; do not assume a round count.** The useful contribution may be where gains saturate and what shifts that point. Unexpectedly smooth improvement warrants checks for contamination and evaluation drift, but is not itself proof of a bug. Predefine the noise statistic and stopping rule; three seeds are a pilot estimate, not a universal significance guarantee.

## Round Discipline

Every round is a logged run under the normal `conventions.md` layout, plus a trajectory record for the loop as a whole:

```
~/research-results/loop-<slug>/
  trajectory.json        one row per round — see below
  noise-floor/           the pre-round-1 seed runs
  round-00/              baseline (the un-improved starting point)
  round-01/  round-02/   … each a standard run directory
```

`trajectory.json` is an object containing `loop` and a `rounds` array, written through `log_run.py trajectory`. Start with round 0 and append exactly one consecutive round at a time; existing rounds cannot be silently replaced. Each entry must point to a completed, citable run directory with `--run-dir`; the helper copies the run's eval identity into the entry and rejects an identity change. It compares the recorded identity strings; it does not recompute or scientifically verify the digest. The primary metric is assumed higher-is-better: transform loss/latency to a declared utility before logging. Each round object looks like:

```json
{
  "round": 3,
  "run_id": "2026-08-14-loop-verifiable-r03",
  "run_dir": "$HOME/research-results/2026-08-14-loop-verifiable-r03",
  "parent_round": 2,
  "parent_run_id": "2026-08-14-loop-verifiable-r02",
  "primary": 0.641,
  "delta": 0.008,
  "noise_floor": 0.011,
  "secondary": 0.512,
  "eval_set": "mathgen-v3",
  "eval_set_sha256": "9f2c000000000000000000000000000000000000000000000000000000000000",
  "n_examples": 4096,
  "cost": {"gpu_hours": 4.2, "dollars": 1.85},
  "cost_per_point": 231.0,
  "human_interventions": 1,
  "constraints": {"diversity": "pass", "tail_coverage": "pass"},
  "verdict": "below noise floor — saturation candidate"
}
```

Rules that keep a long loop honest:

- **Round 0 is the baseline** and gets the same measurement treatment as every other round. The logger rejects a first round with any other number.
- **Every round records its parent and backing run directory.** Accumulate-vs-replace and retrain-from-base-vs-stack are different experiments and get confused constantly when lineage isn't explicit. The logger checks that the backing record is complete and that its `run_id` matches.
- **Never compare rounds measured on different eval sets.** If the eval set or its hash/version changes, the trajectory restarts. The logger compares the copied identity and rejects the append.
- **A round that fails a constraint gate is logged, not deleted.** It is the most informative round in the sweep.
- **Log the eval set's own hash or version** in every round. Silent eval drift produces beautiful fake curves. For a genuinely non-dataset loop, use matching explicit `not-applicable: <reason>` fields in every backing run.

Use the helper with all loop metadata explicit; omitted costs or intervention
counts are not treated as zero:

```bash
log_run.py trajectory ~/research-results/loop-verifiable --round 0 \
  --run-dir ~/research-results/2026-08-14-loop-verifiable-r00 \
  --primary 0.629 --noise-floor 0.011 --secondary 0.510 \
  --gpu-hours 4.2 --dollars 1.85 --human-interventions 1
```

The metrics updater uses an exclusive lock and atomic replacement. A lock left
by an interrupted process is a deliberate stop condition; inspect it before
removing it rather than allowing two writers to merge from stale state.

## Sweeping

One trajectory is an anecdote. The research contribution is usually **many trajectories under varied policy**, which is what turns "it improved" into "here is what governs whether it improves."

Sweep over the choices that plausibly move the saturation point — selection policy, accumulate vs. replace, retrain-from-base vs. stack, capacity — with **one array task = one full loop to round R at a fixed seed and config**. Fixed seed per task, multiple seeds per config, or the noise floor was measured for nothing.

Sweeps are the largest Cost gate in this document. Bring: task count, per-task estimate, total node-hours, and what happens to partial results if the array is killed halfway.

Practical note: a sweep needs the loop to run unattended end to end, which is the same requirement as § Requirements #1. If a human is still in the reward seat, the sweep is not merely expensive — it is impossible. That dependency is worth naming out loud at the design gate, because it usually reorders the work.

## Reporting a Loop

Not "it improved." Report:

1. **The trajectory** — primary score per round, with the noise floor drawn on the same axes. If the error band swallows the curve, say so plainly; that is the result.
2. **Where it saturated**, in rounds, and against the pre-committed criterion.
3. **Cost per unit gain over rounds** — usually the most honest chart in the writeup.
4. **Human-gate load over rounds** — the self-improvement claim lives or dies here.
5. **The secondary axis**, and whether the gap opened.
6. **What moved the saturation point** across the sweep. This is the actual contribution.
7. **Constraint failures**, with the round they occurred at.

And the caveats, unhedged: what was contaminated, what was under-seeded, what you couldn't verify.
