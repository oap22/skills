---
name: rosie
description: "Answer questions about MSOE's ROSIE HPC cluster and Slurm: commands (sbatch, srun, squeue, sacct, scontrol), job scripts, GPU requests (T4, V100, H100), partitions, modules, containers. Use for any ROSIE or Slurm question; dispatching a real run from the Mac is rosie-run."
---

# ROSIE Slurm helper

Answer questions about running work on ROSIE, MSOE's HPC cluster. Give the exact command or job script, then a one-line explanation of each non-obvious flag. Prefer short, copy-pasteable answers.

For dispatching a real experiment from the Mac (pushing code, submitting, polling, pulling results back), use the `rosie-run` skill instead; this one answers Slurm questions and writes job scripts.

## Cluster facts

All cluster facts (host, user, partitions, QoS caps, storage, modules, network) live in one place: `rosie-run/rosie-facts.md`, installed beside this skill. Read it before answering anything that depends on a limit. Key rule: QoS `interactive` caps every job at 1 day and 4 running jobs regardless of partition max (verified 2026-09-17), so `--time` is 1 day or less. The login node is for editing and submitting only; run one-off checks as `ssh rosie 'squeue --me'`.

Live checks:

```bash
sinfo -s                                    # partitions and node counts (A/I/O/T = alloc/idle/other/total)
sinfo -N -o "%N %G %c %m %t"                # per-node GPUs, CPUs, memory, state
sacctmgr -n -P show assoc user=$USER format=account,partition,qos
sacctmgr -n -P show qos interactive format=name,maxwall,maxjobspu
module avail
```

## Everyday commands

```bash
squeue --me                                  # my jobs (ST: PD pending, R running, CG completing)
squeue --me --start                          # estimated start time for pending jobs
squeue -p dgxh100                            # who is on a partition
scancel <jobid>                              # cancel one job
scancel --me                                 # cancel all my jobs
scontrol show job <jobid>                    # full detail, including Reason for pending
sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode
sacct --me -S today                          # today's jobs and exit states
sacct -j <jobid> --format=JobID,Elapsed,TotalCPU,MaxRSS,ReqMem   # efficiency (seff is not installed)
```

## Interactive sessions

```bash
# Shell on a T4 node with one GPU for 2 hours
srun -p teaching --gres=gpu:t4:1 -c 8 --mem=32G -t 02:00:00 --pty bash

# Hold an allocation, then run steps inside it
salloc -p dgx --gres=gpu:v100:1 -c 8 --mem=64G -t 04:00:00
srun nvidia-smi
exit                                          # releases the allocation
```

## Batch job template

```bash
#!/bin/bash
#SBATCH --job-name=train
#SBATCH --partition=teaching          # teaching | batch | highmem | dgx | dgxh100
#SBATCH --gres=gpu:t4:1               # gpu:v100:N on dgx, gpu:h100:N on dgxh100
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=08:00:00               # stay at or under 1-00:00:00 (QoS cap)
#SBATCH --output=logs/%x-%j.out       # %x job name, %j job id; create logs/ first
#SBATCH --error=logs/%x-%j.err

module load cuda/12.9
# For DGX nodes instead: module load h100Env   (or dgx1Env)

source ~/venvs/myenv/bin/activate     # or conda activate / singularity exec
nvidia-smi
python train.py
```

Submit with `sbatch job.sh`. Follow output with `tail -f logs/train-<jobid>.out`.

Container variant:

```bash
module load singularity
singularity exec --nv /data/containers/<image>.sif python train.py   # --nv exposes the GPUs
```

Job arrays: `#SBATCH --array=0-9%4` runs 10 tasks, 4 at a time. Use `$SLURM_ARRAY_TASK_ID` in the script and `%A_%a` in the output filename.

## Picking a partition

- Small or class work, debugging: `teaching` with a T4.
- Needs more than ~358 GB RAM: `highmem`.
- Needs 16-32 GB GPU memory or several fast GPUs: `dgx` (V100).
- Large models, 80 GB GPU memory: `dgxh100` (H100). Only 2 nodes, so expect a wait and request only what you use.

## Debugging pending or failed jobs

Check `squeue --me` for the Reason column, or `scontrol show job <id>`:

- `Resources`: waiting for free nodes/GPUs. Ask for fewer GPUs, less memory, or a less busy partition.
- `Priority`: others are ahead of you. Wait, or shorten `--time` so backfill can fit you in.
- `QOSMaxWallDurationPerJobLimit`: `--time` is over 1 day. Lower it.
- `QOSMaxJobsPerUserLimit`: you already have 4 jobs. Wait or cancel some.
- `ReqNodeNotAvail`: the requested nodes are down or reserved.

For failures, run `sacct -j <id>` for the State and ExitCode:
- `OUT_OF_MEMORY`: raise `--mem`.
- `TIMEOUT`: raise `--time` or checkpoint and resume.
- `CUDA error: no CUDA GPUs`: the job forgot `--gres=gpu:...`.
- `FAILED`: check the `.err` file.

## How to answer

1. If the answer depends on live state (queue, node availability, a specific job), and Bash is available, run the check over `ssh rosie '...'` with `-o BatchMode=yes` and report what you see. Don't guess.
2. Read-only commands (squeue, sinfo, sacct, scontrol show) are fine to run. Ask before `sbatch`, `scancel`, or anything that uses compute time or removes files.
3. If a fact in this file conflicts with live output, trust the live output and mention that this skill needs updating.
