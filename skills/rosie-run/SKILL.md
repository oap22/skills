---
name: rosie-run
description: Dispatch work from this Mac to MSOE's Rosie cluster and bring results back — preflight the VPN and SSH, push code by git, submit an sbatch job or array sweep, poll without babysitting, then pull results back to the Mac's shared results root. Use when Owen says "run this on Rosie", "submit to the cluster", "sbatch this", "run the sweep on ROSIE", "check my Rosie job", or when an experiment is too large for the Mac. Pairs with research-loop, which owns the experiment discipline.
---

# Rosie Run

Rosie is MSOE's cluster. Owen has already run ~2,000 GPU-hours and 3,500+ jobs on it for [[Revit-to-Robot-WACV-2027]], so this skill is not about learning SLURM — it's about making the Mac→Rosie→Mac round trip repeatable and leaving a record that satisfies `research-loop`.

**Host:** `ROSIE` (`dh-mgmt2.hpc.msoe.edu`) · **User:** `pacettio@ad.msoe.edu` · already in `~/.ssh/config`
**Compute nodes:** `dh-node*`, reachable via `ProxyJump ROSIE`

Read `rosie-facts.md` before the first command of any session — it is the accumulated, *verified* knowledge of how this specific cluster behaves, and it is deliberately incomplete. **When you learn something new about Rosie, write it there.**

## The Topology — decided, not up for rediscovery

**The agent runs on the Mac. Rosie is compute and nothing else.**

Skills do not go to Rosie. Claude Code does not go to Rosie. The login node is shared infrastructure, and a long-lived agent process sitting on it is exactly what cluster admins ask people not to do. The only file of ours that crosses is `log_run.py`, which is stdlib-only and version-agnostic for precisely this reason.

If Owen ever asks to run an agent *on* Rosie, that's a real conversation with real prerequisites — treat it as a new decision, not a variation on this one.

## Two Transports, and Why They're Different

| Crossing | Transport | Why |
|---|---|---|
| **Code → Rosie** | `git` (commit, push, pull on Rosie) | The run record has to name a SHA that exists. Rosie has outbound internet, so this works. |
| **Data / results → and ← ** | `rsync` | Large, binary, not version-controlled, often too big for git |

**Code goes over git, not rsync.** This is the rule that keeps `research-loop` honest: `log_run.py` writes a git SHA into `run.json`, and that SHA is worthless if it points at a commit that only ever existed as a working tree on a login node. Rsyncing source is fast and feels convenient, and it silently destroys the provenance chain that makes a result citable months later.

The one exception: **rapid iteration on a script that isn't producing a logged result yet.** Rsync freely while debugging the harness. The moment the run is real, commit, push, pull, and re-run. Say out loud which mode you're in.

## Preflight

Run all of this before anything else. Every step has been the actual cause of a wasted afternoon at some point.

### 1. VPN — the failure that looks like a broken cluster

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 ROSIE 'echo ok'
```

**`Could not resolve hostname` means the MSOE VPN is off, not that Rosie is down.** The hostname only resolves on the campus network. This is the single most common failure and it presents as something scarier than it is.

Owen has to connect the VPN himself — **stop and ask.** Do not attempt to start, configure, or authenticate a VPN client.

### 2. Landing check

```bash
ssh ROSIE 'hostname; whoami; pwd; df -h ~ | tail -1; sinfo -s; squeue -u $USER'
```

Capture: which management node you landed on, home quota and how full it is, available partitions and their state, and anything of yours already queued. **A full home directory fails jobs in ways that look like code bugs** — check the quota number, don't skim past it.

### 3. Pick the partition

Verified 2026-08-12 — full detail and current contention in `rosie-facts.md`:

| Partition | Time limit | Use for |
|---|---|---|
| `teaching` (default) | 7 days | Short jobs, smoke tests, CPU work |
| `batch` | 2 days | General batch |
| `highmem` | 7 days | Memory-bound work (`dh-node[19-20]`) |
| `dgx` | **21 days** | Long GPU runs (3× DGX-1) |
| `dgxh100` | **21 days** | 8× H100/node, 1.9TB RAM, 224 CPUs |

**The 21-day limit on `dgx`/`dgxh100` is what makes a long flywheel run possible** (`OWE-13`). But check contention first — at the 2026-08-12 sweep `dgx` was fully allocated and one of the two H100 nodes was draining, leaving a single usable H100 node. Plan for 8 GPUs, not 16, until `sinfo -p dgxh100` says otherwise.

### 4. Environment discovery — do not assume

Module systems, Python versions, container runtimes, and partition names are cluster-specific and they change. Discover, then record in `rosie-facts.md`:

```bash
ssh ROSIE 'module avail 2>&1 | head -40; echo ---; python3 -V; echo ---; which singularity conda uv 2>&1'
```

As of 2026-08-12: Python 3.12.11 on the login node, `cuda/12.9` default, singularity 3.10.0, miniforge conda, and `uv` at `/snap/bin/uv`.

**The compute nodes run a different Python patch than the login node** — 3.12.10 on `dh-node3` vs 3.12.11 on `dh-mgmt2`. Build environments *inside the job* or use a container; anything validated only against the login interpreter is not guaranteed on a node. (This is why `log_run.py` is stdlib-only, and it ran unmodified on `dh-node3` with zero setup.)

`rosie-facts.md` § Open / Unverified lists what nobody has confirmed yet. **Do not build a job script on an unverified fact** — check it, then record it with the date.

## Cluster Etiquette — non-negotiable

1. **Never compute on the login node.** No training, no data preprocessing, no "quick test" that takes four minutes. It's shared by everyone. Use `srun` for interactive work, `sbatch` for everything else. The login node `dh-mgmt2` has **no GPU at all** (`nvidia-smi` isn't even installed), so GPU code can't be smoke-tested there regardless.
2. **Never `pip install` into a shared or system environment.** Use a project venv under your own storage, or a container.
3. **Ask for what you need, not the maximum.** Over-requesting GPUs or time delays your own job in the queue and everyone else's too.
4. **Always set a time limit.** A job with no wall-clock bound is how a node gets held hostage by a hang.
5. **Clean up scratch.** Large intermediates get deleted when the run is logged, not "later."

## The Round Trip

### 1. Push the code

```bash
git status --porcelain          # must be clean for a logged run
git push
ssh ROSIE 'cd ~/<repo> && git fetch --all && git checkout <sha-or-branch> && git pull && git rev-parse HEAD'
```

**Compare the SHA Rosie reports against your local `HEAD`.** If they differ, you are about to run code you have not read. This check takes two seconds and catches a whole category of confusing results.

**Use SSH remotes, not HTTPS** — verified 2026-08-12. Rosie already has a GitHub SSH key registered for `oap22`, so `git@github.com:oap22/<repo>.git` clones and pulls with no setup. HTTPS against a private repo fails there (no stored credential) and the error reads like a missing repository rather than an auth problem, which sends you debugging the wrong thing.

GitLab is different: the Revit-to-Robot repos live there and the `gitlab-rosie` PAT expired around 2026-04-26 (`OWE-12`, still open). Assume GitLab access from Rosie is broken until that's reissued.

### 2. Stage data with rsync

**Large data goes to `/data`, not home.** `/home` was **97% full** on 2026-08-12 (a 102T filesystem shared by every user, with Owen at 97G of it). Filling it fails your job *and* other people's, and out-of-space on a shared mount surfaces as unrelated crashes rather than a clear error.

```bash
ssh ROSIE 'df -h /home /data'          # ALWAYS before a multi-GB transfer

rsync -avzP --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
      --exclude='.venv' --exclude='research-results' \
      <local-data>/ ROSIE:/data/<...>/
```

`-P` matters: it gives progress and resumes a partial transfer instead of restarting a multi-GB copy from zero.

**Never ship the local results root up.** It lives outside every repo now (`~/research-results`), so it usually isn't inside the tree you're syncing anyway — but if you're rsyncing from `~`, exclude it. Rosie writes its own results into its own `~/research-results`; pushing the Mac's copy up would overwrite fresh cluster output with stale local output and cost you the transfer twice.

There is **no `quota` command** on Rosie — capacity questions are answered with `df`. Don't reach for `du -sh ~` either; it takes over two minutes on this filesystem. Background it if you truly need it.

### 3. Submit

Templates are in `templates/`. Copy, fill, submit — never write one from scratch, and never submit one with a placeholder still in it.

```bash
scp templates/job.sbatch ROSIE:~/<repo>/jobs/
ssh ROSIE 'cd ~/<repo> && sbatch jobs/job.sbatch'   # prints the job ID — record it
```

**The job script runs `log_run.py` inside the job**, so the record is written where the compute happened, with the real SLURM IDs captured (`log_run.py` picks up `SLURM_JOB_ID` and `SLURM_ARRAY_TASK_ID` into `run.json` automatically). Do not run the experiment bare and reconstruct a record afterward.

**→ COST GATE.** Before submitting anything nontrivial, state: number of tasks, GPUs and wall-clock requested per task, total node-hours, and what happens to partial results if the array is cancelled halfway. For a sweep this is the largest gate in the whole workflow — see `research-loop/driving-functions.md` § Sweeping.

### 4. Poll — don't babysit

```bash
ssh ROSIE 'squeue -u $USER -o "%.10i %.9P %.20j %.8T %.10M %.6D %R"'
```

Poll on a **cadence matched to the job**, not every thirty seconds. A four-hour training run does not need checking every minute; it needs checking every twenty. Between polls, do other work or hand control back.

For a long job, the honest move is to tell Owen the job ID and expected completion, and stop — rather than burning a session watching a queue.

Reading logs mid-flight:

```bash
ssh ROSIE 'tail -40 ~/<repo>/logs/slurm-<jobid>.out'
```

When a job fails, get the real reason before theorizing:

```bash
ssh ROSIE 'sacct -j <jobid> --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS,ReqTRES -P'
```

`OUT_OF_MEMORY`, `TIMEOUT`, and `NODE_FAIL` are the common three and they demand different fixes. Guessing between them wastes another queue cycle.

### 5. Pull results back

Results land in the **Mac's shared results root** — Rosie is scratch, not the archive.

```bash
rsync -avzP --exclude='artifacts/' \
      ROSIE:~/research-results/ ~/research-results/
```

Both sides use the same home-anchored path, because `log_run.py` defaults there on the cluster too. Landing in `~/research-results/` is also what makes the run appear in the Turing desktop's metrics, images and flywheel panes — pull into the repo instead and the charts stay dead. For a long job, pull mid-flight (or use the `ssh-pull-assets` / `ssh-follow-metrics` desktop runners) and Owen watches the cluster run live.

Excluding `artifacts/` by default is deliberate: checkpoints and large binaries stay on the cluster until Owen asks for a specific one. The record — `run.json`, `metrics.json`, `metrics.jsonl`, `stdout.log`, `notes.md`, `trajectory.json` — plus the SVG/PNG plots the panes render is small and comes back every time.

Then **validate before citing anything**:

```bash
LOG_RUN=$(ls ~/.claude/skills/research-loop/log_run.py \
             ~/.cursor/skills/research-loop/log_run.py \
             ~/Developer/active/skills/skills/research-loop/log_run.py \
             2>/dev/null | head -1)
python3 "$LOG_RUN" check ~/research-results/<run-id>
```

(The script's install path differs per harness — resolve it the way `research-loop` § Invoking log_run.py does, never assume one harness's path.)

A run that fails `check` is not a result yet. Fix the record or label it unverified — do not write it into the journal as fact.

### 6. Log it

Hand back to `research-loop`: journal entry, estimate vs. actual (SLURM's `Elapsed` from `sacct` is the ground truth for the actual), dead-ends if the run ruled something out, and the vault digest.

Node-hours consumed belong in the entry. For a self-improving loop, they are the denominator in cost-per-unit-gain, and reconstructing them later from memory is impossible.

## Sweeps

A sweep is a SLURM **array job**: one array task = one full configuration at a fixed seed. `templates/array.sbatch` is the starting point.

Rules that keep a sweep interpretable:

- **One array task = one complete unit of work.** For a self-improving loop that means one full flywheel to round *R* — not one round, or lineage across tasks becomes unreconstructable.
- **Fixed seed per task, multiple seeds per config.** Otherwise the noise floor was measured for nothing.
- **Write results to a per-task directory** keyed by `SLURM_ARRAY_TASK_ID`. Concurrent tasks writing one file corrupt it, and the corruption is silent.
- **Throttle with `%`** (`--array=0-63%8`) to cap concurrent tasks. Uncapped, you take the whole partition and make enemies.
- **Log what was dropped.** If tasks fail, say how many and which. A sweep reported as complete when 12 of 64 tasks died is a false result.

## Never

- Start the VPN, or touch VPN configuration. Ask Owen.
- Run compute on the login node.
- Submit a job whose cost you haven't stated.
- Rsync source code for a run that will be logged as a result.
- Cite a run whose Rosie SHA didn't match local `HEAD`.
- Delete anything from Rosie storage without asking — cluster home directories are not backed up the way you'd hope.
- Write a fact into `rosie-facts.md` you did not observe in command output.
