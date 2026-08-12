#!/bin/bash
# Single job — copy, fill every <...>, submit. Never submit with a placeholder left in.
# Verified against Rosie 2026-08-12 (SLURM 23.11.6). See rosie-facts.md.

#SBATCH --job-name=<name>
#SBATCH --partition=<teaching|batch|highmem|dgx|dgxh100>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=<n>
#SBATCH --gres=gpu:<n>              # drop entirely for CPU-only work; h100 nodes are gpu:h100:8
#SBATCH --time=<D-HH:MM:SS>         # ALWAYS set one. teaching/highmem 7d, batch 2d, dgx* 21d
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.out

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
mkdir -p logs

# --- environment: build it in the job, not on the login node ---------------
# The compute nodes run a different Python patch than dh-mgmt2 (3.12.10 vs
# 3.12.11 as of 2026-08-12), so anything validated only on login is unproven.
module load cuda/12.9                     # or dgx1Env / h100Env for those partitions
# source .venv/bin/activate               # uv is at /snap/bin/uv
# singularity exec --nv <image.sif> ...   # singularity 3.10.0

echo "node=$(hostname) job=$SLURM_JOB_ID"
nvidia-smi -L || true                     # absent on the login node; present here

# --- the run ---------------------------------------------------------------
# log_run.py records the git SHA, env, timing, stdout, exit code, and picks up
# SLURM_JOB_ID automatically. Run the experiment THROUGH it, never beside it.
python3 log_run.py run \
    --name <run-slug> \
    --config <configs/thing.yaml> \
    --estimate-minutes <n> \
    -- <the actual command>

# Results land in research/results/<date>-<run-slug>/.
# Pull them back to the Mac with rsync; do not archive on Rosie.
