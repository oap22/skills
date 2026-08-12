# Research Loop — Conventions

The on-disk spec. Read before writing anything under `research/`.

The whole point of a convention here is **comparability across time**. A results directory written in August has to be readable, diffable, and re-runnable in March by someone who remembers nothing. That is the only test that matters; every rule below serves it.

## Layout

```
research/
  JOURNAL.md              reverse-chronological narrative — the thread
  OPEN-QUESTIONS.md       what we don't know yet
  DEAD-ENDS.md            what's been ruled out, one line each
  results/
    2026-08-14-lr-sweep-cosine/     one directory per run
      run.json                      metadata — written by log_run.py
      config.yaml                   the exact config used (copied, not referenced)
      metrics.json                  the numbers
      stdout.log                    everything the command printed
      notes.md                      the human-readable record
      artifacts/                    plots, checkpoints, large outputs — gitignored
    loop-verifiable-retarget/       self-improving loops — see driving-functions.md
      trajectory.json
      noise-floor/  round-00/  round-01/  …
```

## Run IDs

`YYYY-MM-DD-<slug>`, slug in kebab-case, descriptive of the *question* not the tool: `lr-sweep-cosine`, not `train-run-3`. Same-day collisions get `-b`, `-c` suffixes. The ID is the primary key — journal entries, plots, and writeups all cite it, so it never changes once written.

## run.json

Written by `log_run.py`; never hand-edit. Records what the run *was*, as distinct from what it *found*:

| Field | Why it's there |
|---|---|
| `run_id`, `name`, `command` | Identity and the literal argv |
| `git.sha`, `git.branch`, `git.dirty`, `git.diff_stat` | Which code ran. `dirty: true` is a caveat on every number in the run |
| `started_at`, `finished_at`, `duration_seconds` | Wall clock |
| `estimate_minutes`, `estimate_error_ratio` | Estimate vs. actual — calibration over time |
| `exit_code` | Non-zero means the metrics are suspect, full stop |
| `env` | Python version, platform, hostname, key package versions |
| `config_path`, `config_sha256` | Ties the copied config to its original |

**A run with a non-zero exit code is never cited as a result.** It gets logged — failures are data — but it is not evidence for a claim.

## metrics.json

Flat where possible. Scalars are the point; nested structures should be rare and deliberate.

```json
{
  "held_out_accuracy": 0.641,
  "train_loss_final": 0.212,
  "eval_set": "mathgen-v3",
  "eval_set_sha256": "9f2c…",
  "seed": 1337,
  "n_examples": 4096
}
```

Always include **`seed`**, **`n_examples`**, and an **eval set identifier plus hash**. A metric without its seed can't be compared; a metric without its eval set version silently drifts and produces a beautiful fake curve.

## notes.md

The human layer of the run directory. Short:

```markdown
# 2026-08-14-lr-sweep-cosine

**Question:** Does cosine decay beat step decay at this budget?
**Answer:** Yes — +1.2pp held-out, outside the ±0.4pp seed band.

## Verification
- Re-ran at seeds 7, 42, 1337 — spread ±0.4pp, effect survives
- Control (step decay) run through the identical harness: 2026-08-14-lr-sweep-step
- Sanity: hand-checked accuracy on 20 examples, matches reported

## Caveats
- Single dataset. No claim beyond it.
- Tree was dirty at run time (see run.json) — uncommitted plotting change only.
```

## JOURNAL.md

Newest entry at the top, immediately under the header. Never edit or delete a past entry — a wrong entry gets **corrected by a new entry linking back**, because the record of having been wrong is part of the record.

```markdown
## 2026-08-14 — Cosine vs. step decay

**Hypothesis:** Cosine decay improves held-out accuracy at fixed compute.
**Measurement:** Held-out accuracy on mathgen-v3, 3 seeds.
**Control:** Step decay, identical harness.
**Falsifier:** Difference inside the seed band.

**Result:** +1.2pp (0.629 → 0.641), seed band ±0.4pp. → `results/2026-08-14-lr-sweep-cosine/`

**Verified by:** 3 seeds · control through identical path · hand-check of 20 examples.
**Not verified:** Generalization past mathgen-v3.

**Estimate vs. actual:** 45 min est · 62 min actual (1.4×) — underestimated eval time.

**Decision:** Cosine becomes the default. Step decay → DEAD-ENDS.
**Raised:** Does the gap hold at 4× budget? → OPEN-QUESTIONS.
```

Entries for **negative results are written with the same care as positive ones**, and additionally get a line in `DEAD-ENDS.md`. This is the highest-value habit in the whole skill: nobody publishes what didn't work, so everybody re-runs it.

## DEAD-ENDS.md

Grep-optimized. One line per ruled-out thing, so a future session can check it in seconds:

```markdown
- **Step LR decay** — 1.2pp worse than cosine at fixed budget. `2026-08-14-lr-sweep-step`. Not worth re-testing below 4× budget.
- **Batch size 512** — OOM on 8GB Jetson at Q4. Hardware limit, not a tuning problem. `2026-08-11-bs-sweep`.
```

Format: what was tried · why it failed · run ID · **what would make it worth revisiting**. That last clause is what separates a dead end from a permanent prohibition.

## OPEN-QUESTIONS.md

```markdown
- [ ] Does the cosine gap hold at 4× compute? — raised 2026-08-14, blocked on ROSIE access (OWE-13)
- [x] Is mathgen-v3 contaminated? — answered 2026-08-12, no: generated post-cutoff. `2026-08-12-contam-check`
```

Answered questions stay, checked, with the run that settled them. The list is a map of what's known, not a to-do.

## Version Control

Commit the record. Never commit the artifacts.

```gitignore
research/results/**/artifacts/
research/results/**/*.ckpt
research/results/**/*.pt
research/results/**/*.safetensors
research/results/**/*.parquet
```

`run.json`, `config.yaml`, `metrics.json`, `notes.md`, `stdout.log`, and `trajectory.json` are small, diffable, and the entire point — they get committed. If `stdout.log` is enormous, truncate the middle and say so in the file rather than gitignoring it.

**Commit the code before a run that matters.** `log_run.py` records dirty state and warns; it won't stop you, and a dirty tree is a caveat attached to every number the run produced.

## Vault Digest

The repo is the source of truth. The vault gets **conclusions**, at natural boundaries — a question answered, a direction abandoned, a milestone hit — not an entry-by-entry mirror. `research-ingest` exists because mirroring rots.

Update the project note under `02-Projects/`, following `.system/agent-conventions.md`: wikilinks not markdown links, append over rewrite, never delete. Include the run ID so the vault points back at the repo, and keep the repo path in the note's frontmatter.

## Notebooks

Notebooks live wherever they already live and are exempt from all of the above — they're scratch. The moment a notebook result matters it graduates to a script and gets logged like anything else. A notebook result that hasn't graduated is reported as **provisional** and never enters `JOURNAL.md` as fact.
