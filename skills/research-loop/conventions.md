# Research Loop — Conventions

The on-disk spec. Read before writing anything under `research/`.

The whole point of a convention here is **comparability across time**. A results directory written in August has to be readable, diffable, and re-runnable in March by someone who remembers nothing. That is the only test that matters; every rule below serves it.

## Layout

The narrative lives in the repo. The runs live in a **shared results root outside every repo** — `~/research-results` by default (`--results-dir`, or `RESEARCH_RESULTS_ROOT`, repoints it). Home-anchored rather than repo-relative so research code can sit in any project and still land where the Turing desktop app watches for metrics and plots, without dropping untracked artifacts into that project's checkout.

```
research/                 in the repo, version-controlled
  JOURNAL.md              reverse-chronological narrative — the thread
  OPEN-QUESTIONS.md       what we don't know yet
  DEAD-ENDS.md            what's been ruled out, one line each

~/research-results/       the shared results root, outside any repo
  2026-08-14-lr-sweep-cosine/     one directory per run
    run.json                      metadata — written by log_run.py
    config.yaml                   the exact config used (copied, not referenced)
    metrics.json                  the numbers
    metrics.jsonl                 optional per-step stream — see below
    stdout.log                    everything the command printed
    notes.md                      the human-readable record
    artifacts/                    plots, checkpoints, large outputs
  loop-verifiable-retarget/       self-improving loops — see driving-functions.md
    trajectory.json
    noise-floor/  round-00/  round-01/  …
```

Runs are just directories: the desktop panes discover them by walking the root, so nothing needs registering, and deleting a directory makes it disappear.

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
| `env` | Wrapper Python version, platform, hostname, ambient packages; experiment environment recorded separately |
| `config_path`, `config_sha256` | Ties the copied config to its original |

`log_run.py check` requires `git.available: true`, a 40- or 64-character Git
object ID in the expected shape, a branch name, ISO-8601 start and finish
timestamps, and a nonempty command list. A record made outside a Git checkout
remains useful for debugging but is not citable; rerun it from a committed Git
checkout before citing it. These checks validate field shape and presence only:
they do not prove that the Git object exists locally or that the dataset digest
matches the scientific data.

**A run with a non-zero exit code is never cited as a result.** It gets logged — failures are data — but it is not evidence for a claim.

## metrics.json

Flat where possible. Scalars are the point; nested structures should be rare and deliberate.

**Live streaming (Turing desktop):** *additionally* append per-step lines to `metrics.jsonl` in the same run directory (`{"step": n, "total_steps": N, "ts": epoch, ...numeric series}`) — the Turing desktop app tails it and charts the run live. This works from any project, not just the Turing repo, because the run directory already sits in the watched root. The final `metrics.json` above stays the citable artifact; the JSONL is visibility, not evidence. See the `turing` skill.

```json
{
  "held_out_accuracy": 0.641,
  "train_loss_final": 0.212,
  "eval_set": "mathgen-v3",
  "eval_set_sha256": "9f2c000000000000000000000000000000000000000000000000000000000000",
  "seed": 1337,
  "n_examples": 4096
}
```

Always include **`seed`**, **`n_examples`**, and **`eval_set` / `eval_set_sha256`**. `seed` and `n_examples` are nonnegative integers; `eval_set` is a nonempty string; and `eval_set_sha256` is a 64-character hexadecimal SHA-256 digest. For non-dataset or deterministic runs, use an explicit `not-applicable: <reason>` value for each inapplicable field, and use it consistently for `eval_set` and `eval_set_sha256`; never fabricate provenance. A metric without its seed can't be compared; a metric without its eval set version silently drifts and produces a beautiful fake curve. `log_run.py check` rejects wrong types, nonfinite values, malformed hashes, and symlinked citation files.

The `metrics` subcommand serializes its read/modify/write cycle with an
exclusive `.metrics.json.lock` beside the file, then replaces the file
atomically. If a process dies while holding the lock, later writers wait briefly
and fail without deleting it. Inspect the owner and remove that lock manually
only after confirming no writer remains; stale-lock recovery is intentionally
not automatic.

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

**Result:** +1.2pp (0.629 → 0.641), seed band ±0.4pp. → `~/research-results/2026-08-14-lr-sweep-cosine/`

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
- [ ] Does the cosine gap hold at 4× compute? — raised 2026-08-14, blocked on ROSIE access (formerly OWE-13)
- [x] Is mathgen-v3 contaminated? — answered 2026-08-12, no: generated post-cutoff. `2026-08-12-contam-check`
```

Answered questions stay, checked, with the run that settled them. The list is a map of what's known, not a to-do.

## Version Control

The run directories are no longer inside the repo, so the repo's history no longer carries the record automatically — and that is a real loss to compensate for, not a detail. Two rules replace the old gitignore stanza:

1. **The journal is the committed artifact.** `JOURNAL.md`, `OPEN-QUESTIONS.md`, and `DEAD-ENDS.md` live in the repo and cite run IDs. A run ID that appears in a committed entry is what makes the result findable later; a result that exists only as a directory under `~/research-results` and is named nowhere in git is one `rm -rf` from never having happened.
2. **When a run backs a claim that matters, copy its small files into the repo** — `run.json`, `config.yaml`, `metrics.json`, `notes.md`, `stdout.log`, `trajectory.json` — to `research/records/<run-id>/`, unless the project already has a home for them, and commit them alongside the journal entry. They're small, diffable, and the entire point. If `stdout.log` is enormous, truncate the middle and say so in the file rather than dropping it.

Never copy `artifacts/` into the repo — checkpoints and other large binaries stay in the results root, where they are outside git by construction. That is the one thing this layout makes easier: committing 4GB of checkpoints is now something you'd have to do on purpose.

If Owen wants the whole results root under version control, `git init` in `~/research-results` itself is the move — one history for every project's runs — with this stanza in its `.gitignore`:

```gitignore
**/artifacts/
**/*.ckpt
**/*.pt
**/*.safetensors
**/*.parquet
```

**Commit the code before a run that matters.** `log_run.py` records dirty state and warns; it won't stop you, and a dirty tree is a caveat attached to every number the run produced.

## Vault Digest

The repo is the source of truth. The vault gets **conclusions**, at natural boundaries — a question answered, a direction abandoned, a milestone hit — not an entry-by-entry mirror. `research-ingest` exists because mirroring rots.

Update the project note under `02-Projects/`, following `.system/agent-conventions.md`: wikilinks not markdown links, append over rewrite, never delete. Include the run ID so the vault points back at the repo, and keep the repo path in the note's frontmatter.

## Notebooks

Notebooks live wherever they already live and are exempt from all of the above — they're scratch. The moment a notebook result matters it graduates to a script and gets logged like anything else. A notebook result that hasn't graduated is reported as **provisional** and never enters `JOURNAL.md` as fact.
