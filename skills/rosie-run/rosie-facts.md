# Rosie — Verified Facts

Everything here was **observed in command output**, not assumed. Each block carries the date it was checked. Clusters change; re-verify anything older than a few months and update the date.

**Rule: never add a fact to this file you did not see in real output.** A confident wrong fact about a cluster costs a queue cycle to discover.

Last full sweep: **2026-08-12** (from Owen's Mac, on MSOE VPN).

## Access

| | |
|---|---|
| SSH host alias | `ROSIE` → `<login-node>` (already in `~/.ssh/config`) |
| User | `<cluster-user>` |
| Home | `$HOME` |
| Login node | `dh-mgmt2` — **no GPU** (`nvidia-smi` is not installed) |
| Compute nodes | `dh-node[1-20]`, `dh-dgx1-[1-3]`, `dh-dgxh100-[1-2]` — via `ProxyJump ROSIE` |
| Requires | **MSOE VPN when off campus.** Without it the hostname does not resolve. |
| SLURM | 23.11.6 |
| Account / QOS | account `students`, QOS `interactive` |

**`Could not resolve hostname <login-node>` means the VPN is off.** It is not a cluster outage. Verified 2026-08-12 — this exact failure occurred before the VPN was connected, and connecting it fixed it.

## Partitions — verified 2026-08-12

```
PARTITION  TIMELIMIT   NODES  NODELIST
teaching*  7-00:00:00  20     dh-node[1-20]      ← default
batch      2-00:00:00  20     dh-node[1-20]
highmem    7-00:00:00  2      dh-node[19-20]
desktop    7-00:00:00  20     dh-node[1-20]
dgx        21-00:00:0  3      dh-dgx1-[1-3]
dgxh100    21-00:00:0  2      dh-dgxh100-[1-2]
```

`teaching` is the default and takes anything short. **`dgx` and `dgxh100` allow 21-day jobs** — that is the home for a long flywheel run (`OWE-13`).

**dgxh100 detail:** `gpu:h100:8` per node · 1,960,812 MB RAM · 224 CPUs. At the 2026-08-12 check `dh-dgxh100-1` was `mix` and `dh-dgxh100-2` was `drain` — i.e. **one usable H100 node**, so contention is real. Check `sinfo -p dgxh100` before planning around 16 GPUs; you may only have 8.

`dgx` was fully allocated (3/3) at the same check.

## Storage — verified 2026-08-12

| Mount | Size | Used | Note |
|---|---|---|---|
| `/home` (`dh-netapp1_1`) | 102T | **97%** | Shared across all users. Effectively full. |
| `/data` (`dh-netapp1_2:/more_data`) | 181T | 83% | Where large data belongs |
| `/scratch` | — | — | Exists; capacity not yet measured |

**Owen's home usage: 97G** (2026-08-12). `quota` is **not installed** on Rosie, so there is no per-user quota command — capacity questions are answered with `df` against the shared mount, and your own footprint with a (slow) `du`.

**`/home` was at 97% on 2026-08-12.** This is the highest-risk fact in the file. A large rsync into home can fail mid-transfer or fail *someone else's* job, and out-of-space failures on a shared filesystem present as unrelated crashes. **Stage datasets and checkpoints under `/data`, not home.** Check `df -h /home /data` before any multi-GB transfer.

Do not run `du -sh ~` casually — on this networked filesystem it took **over two minutes** to return (measured 2026-08-12). If you need it, background it; never block a session on it. Use `df` for capacity questions.

## Software — verified 2026-08-12

| | |
|---|---|
| Python (login `dh-mgmt2`) | 3.12.11 |
| Python (compute `dh-node3`) | **3.12.10** — *not identical to login* |
| git | `/usr/bin/git` |
| rsync | `/usr/bin/rsync` |
| singularity | 3.10.0 (`/usr/local/singularity-3.10.0/bin/singularity`) |
| conda | miniforge3 (`/usr/local/miniforge/miniforge3/bin/conda`) |
| uv | `/snap/bin/uv` |

**The login and compute nodes run different Python patch versions.** Anything built against the login node's interpreter is not guaranteed to behave identically on a node. Build environments *inside the job*, or use a container. This is exactly why `log_run.py` is stdlib-only — verified running on `dh-node3` under 3.12.10 with no setup.

### Modules (`module avail`)

```
StdEnv (L)            cuda/current (L)   cuda/10.1  cuda/11.7  cuda/12.1
cuda/12.5             cuda/12.9 (D)      dgx1Env    h100Env
openmpi/4.0.1  4.1.4  openmpi/current (L)           openmpi/4.0.1.cuda-10.1
singularity/current (L)  singularity/3.3.0  3.7.1  3.10.0 (D)
matlab/current (L)    matlab/R2022a      matlab/R2024b (D)
```

`cuda/12.9` is the default; `dgx1Env` and `h100Env` exist for the respective GPU partitions and are the first thing to try when targeting them.

## Network — verified 2026-08-12

| Test | Result |
|---|---|
| `curl -sI https://api.github.com` | **OK** — general outbound HTTPS works |
| `ssh -T git@github.com` | **OK** — authenticates as `oap22` |
| `git ls-remote https://github.com/oap22/agent-skills.git` | **FAILED** — private repo over HTTPS has no credential |

**Use SSH remotes on Rosie, not HTTPS.** A GitHub SSH key for `oap22` is already registered from Rosie, so `git@github.com:` clones and pulls work today with no setup. HTTPS fails on private repos because there's no stored token, and the error looks like a missing repo rather than an auth problem.

**GitLab is a separate story.** The Revit-to-Robot repos are on GitLab, and the `gitlab-rosie` PAT expired around 2026-04-26 (`OWE-12`, still open). GitLab access from Rosie is presumed broken until that's reissued — **not yet re-tested.**

## Verified Round Trip — 2026-08-12

A full Mac→Rosie→Mac cycle was run end to end (job `271632`, `teaching` partition, `dh-node3`, 4 s elapsed, exit 0):

1. `scp` of `log_run.py` → 2. `sbatch` → 3. poll to completion → 4. `sacct` confirmed `COMPLETED 0:0` → 5. `rsync` results back → 6. local `log_run.py check`.

Confirmed working: `log_run.py` runs unmodified on a compute node · `SLURM_JOB_ID` is captured into `run.json` automatically · results rsync back intact · `check` correctly **rejected** the run for having no git SHA and an unfilled `notes.md`.

**`SLURM_ARRAY_TASK_ID` capture has not been exercised on a real array job yet** — the smoke test was a single job. Verify on the first real sweep.

The smoke-test directory was removed from Rosie afterward.

## Open / Unverified

- `/scratch` capacity, purge policy, and whether it's node-local or shared
- Per-user quota policy — `quota` is not installed, so whether a per-user limit is even enforced is unknown
- GitLab access after the `gitlab-rosie` PAT is reissued (`OWE-12`)
- Array-job behavior end to end, including `%` throttling
- Whether `dgxh100` requires a reservation or special account beyond QOS `interactive`
- Real GPU job: nothing in this file has yet been verified on a node with a GPU attached
