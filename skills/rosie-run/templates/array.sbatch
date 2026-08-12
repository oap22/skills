#!/bin/bash
# Array sweep — one task = ONE COMPLETE unit of work.
# For a self-improving loop that means one full flywheel to round R at a fixed
# seed, not one round. Splitting rounds across tasks makes lineage
# unreconstructable. See research-loop/driving-functions.md § Sweeping.

#SBATCH --job-name=<sweep-name>
#SBATCH --partition=<dgx|dgxh100|teaching>
#SBATCH --array=0-<N>%<concurrent>   # the % throttle is not optional — uncapped
                                     # arrays take the whole partition
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=<n>
#SBATCH --gres=gpu:<n>
#SBATCH --time=<D-HH:MM:SS>
#SBATCH --output=logs/slurm-%A_%a.out
#SBATCH --error=logs/slurm-%A_%a.out

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
mkdir -p logs

module load cuda/12.9

TASK=${SLURM_ARRAY_TASK_ID}

# --- map task index -> configuration --------------------------------------
# Keep this mapping in a committed file, not inline arithmetic. Six weeks from
# now "task 37" has to resolve to an exact configuration, and a shell
# expression nobody can re-derive is how a sweep becomes uninterpretable.
CONFIG=$(sed -n "$((TASK + 1))p" sweep-configs.txt)
SEED=$(echo "$CONFIG" | cut -d' ' -f1)

echo "task=$TASK config=$CONFIG node=$(hostname) job=$SLURM_ARRAY_JOB_ID"

# --- per-task output directory --------------------------------------------
# Concurrent tasks writing one file corrupt it, and the corruption is silent.
python3 log_run.py run \
    --name "<sweep-name>-t${TASK}" \
    --config "$CONFIG" \
    --estimate-minutes <n> \
    -- <the actual command> --seed "$SEED"

# After the array finishes:
#   1. sacct -j <arrayjobid> --format=JobID,State,ExitCode,Elapsed -P
#      -> count failures. A sweep reported complete with 12 of 64 tasks dead
#         is a false result. Say how many were dropped.
#   2. rsync results back to the Mac
#   3. log_run.py trajectory ... for each round of each loop
