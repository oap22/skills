#!/usr/bin/env python3
"""log_run.py — run an experiment and leave a complete record behind.

The point is that a run cannot be *half*-logged. Wrapping the command means the
git SHA, environment, timing, stdout, and exit code are captured by construction
rather than reconstructed afterward from memory.

    # run and log in one step (the normal path)
    log_run.py run --name lr-sweep-cosine --config configs/sweep.yaml \
        --estimate-minutes 45 -- python train.py --config configs/sweep.yaml

    # record metrics after the fact (or from inside your own code)
    log_run.py metrics ~/research-results/2026-08-14-lr-sweep-cosine \
        --set held_out_accuracy=0.641 --set seed=1337

    # validate a run directory before citing it in the journal
    log_run.py check ~/research-results/2026-08-14-lr-sweep-cosine

    # append a round to a self-improving loop's trajectory
    log_run.py trajectory ~/research-results/loop-verifiable --round 3 \
        --run-id 2026-08-14-loop-r03 --primary 0.641 --noise-floor 0.011 \
        --gpu-hours 4.2 --dollars 1.85 --human-interventions 1

Stdlib only, so it runs anywhere Python does.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import tempfile
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

# The shared results root is home-anchored rather than repo-relative: research
# code can live in any project and still land where the Turing desktop app
# watches for metrics and plots. Repoint per-run with --results-dir.
RESULTS_DIR = Path(
    os.environ.get("RESEARCH_RESULTS_ROOT")
    or os.environ.get("TURING_RESEARCH_RESULTS_ROOT")
    or (Path.home() / "research-results")
).expanduser()
REQUIRED_FOR_CITATION = ("run.json", "metrics.json", "notes.md")


# ---------------------------------------------------------------- helpers


def _sh(*args: str) -> str:
    """Run a command, return stripped stdout, empty string on any failure."""
    try:
        out = subprocess.run(
            args, capture_output=True, text=True, timeout=30, check=False
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def git_state() -> dict:
    if not _sh("git", "rev-parse", "--is-inside-work-tree") == "true":
        return {"available": False}
    dirty_files = _sh("git", "status", "--porcelain")
    return {
        "available": True,
        "sha": _sh("git", "rev-parse", "HEAD"),
        "branch": _sh("git", "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(dirty_files),
        "dirty_files": dirty_files.splitlines()[:50],
        "diff_stat": _sh("git", "diff", "--stat"),
    }


def env_state() -> dict:
    env = {
        "wrapper_python": sys.version.split()[0],
        "packages_scope": "wrapper/ambient environment; experiment must record its own interpreter and dependencies",
        "platform": platform.platform(),
        "hostname": platform.node(),
        "cwd": os.getcwd(),
    }
    # Freeze the package set when we can — it is the most common hidden confound.
    for cmd in (["uv", "pip", "freeze"], [sys.executable, "-m", "pip", "freeze"]):
        if shutil.which(cmd[0]) or cmd[0] == sys.executable:
            frozen = _sh(*cmd)
            if frozen:
                env["packages"] = frozen.splitlines()
                break
    for var in ("CUDA_VISIBLE_DEVICES", "SLURM_JOB_ID", "SLURM_ARRAY_TASK_ID"):
        if var in os.environ:
            env[var] = os.environ[var]
    return env


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def allocate_dir(name: str, root: Path) -> Path:
    """<results-root>/YYYY-MM-DD-<slug>, suffixed on same-day collision."""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise SystemExit("--name must be a kebab-case slug, not a path")
    stem = f"{date.today().isoformat()}-{name}"
    root.mkdir(parents=True, exist_ok=True)
    for suffix in [""] + [f"-{x}" for x in "bcdefghijklmnopqrstuvwxyz"]:
        candidate = root / f"{stem}{suffix}"
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
    raise SystemExit(f"too many runs named {stem} today; pick a different --name")


def coerce(value: str):
    """'0.64' -> float, '12' -> int, 'true' -> bool, else str."""
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    for cast in (int, float):
        try:
            result = cast(value)
            if isinstance(result, float) and not math.isfinite(result):
                raise SystemExit("metrics must be finite; NaN/Infinity are not results")
            return result
        except ValueError:
            pass
    return value


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"nonfinite value: {x}")))
    except (OSError, ValueError) as exc:
        raise ValueError(f"{path.name}: invalid JSON: {exc}") from exc
    json.dumps(value, allow_nan=False)  # also reject overflow literals such as 1e309
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected a JSON object")
    return value


def dump_json(path: Path, payload) -> None:
    encoded = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


# ---------------------------------------------------------------- run


NOTES_TEMPLATE = """# {run_id}

**Question:** <what this run was meant to settle>
**Answer:** <fill in after verifying — not before>

## Verification
<which checks from SKILL.md § Verify you actually did, and what they showed>

## Caveats
<what this does NOT show. An empty section here is almost always a lie.>
"""


def cmd_run(args: argparse.Namespace) -> int:
    if args.config and not Path(args.config).is_file():
        raise SystemExit(f"config not found: {args.config}")
    root = Path(args.results_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_dir = allocate_dir(args.name, root)
    (run_dir / "artifacts").mkdir(parents=True)

    git = git_state()
    if git.get("dirty"):
        print(
            f"WARNING: git tree is dirty ({len(git['dirty_files'])} file(s)). "
            "This is recorded in run.json and is a caveat on every number this "
            "run produces. Commit first if the result matters.",
            file=sys.stderr,
        )

    record = {
        "run_id": run_dir.name,
        "name": args.name,
        "command": args.command,
        "started_at": now(),
        "estimate_minutes": args.estimate_minutes,
        "git": git,
        "env": env_state(),
        "notes": args.note,
    }

    if args.config:
        src = Path(args.config)
        if not src.exists():
            raise SystemExit(f"config not found: {src}")
        shutil.copy2(src, run_dir / f"config{src.suffix or '.yaml'}")
        record["config_path"] = str(src)
        record["config_sha256"] = sha256(src)

    dump_json(run_dir / "run.json", record)
    (run_dir / "notes.md").write_text(NOTES_TEMPLATE.format(run_id=run_dir.name))

    print(f"[log_run] {run_dir}")
    print(f"[log_run] $ {' '.join(args.command)}\n", flush=True)

    started = time.monotonic()
    log_path = run_dir / "stdout.log"
    with log_path.open("w") as log:
        log.write(f"$ {' '.join(args.command)}\n\n")
        log.flush()
        try:
            proc = subprocess.Popen(
                args.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                errors="replace",
                env={**os.environ, "RESEARCH_RUN_DIR": str(run_dir)},
            )
        except OSError as exc:
            record.update(finished_at=now(), duration_seconds=round(time.monotonic() - started, 2), exit_code=127, launch_error=str(exc))
            dump_json(run_dir / "run.json", record)
            log.write(f"Launch failed: {exc}\n")
            print(f"[log_run] launch failed: {exc}", file=sys.stderr)
            return 127
        # Tee: the operator watches it live, the file keeps it forever.
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            log.write(line)
        exit_code = proc.wait()

    duration = time.monotonic() - started
    record.update(
        finished_at=now(),
        duration_seconds=round(duration, 2),
        exit_code=exit_code,
    )
    if args.estimate_minutes:
        record["estimate_error_ratio"] = round(
            duration / 60 / args.estimate_minutes, 2
        )

    # Only the allocated run directory belongs to this run. Never claim or move
    # a metrics.json left in the caller's working directory by an earlier run.
    dump_json(run_dir / "run.json", record)

    print(f"\n[log_run] exit {exit_code} · {duration / 60:.1f} min · {run_dir}")
    if args.estimate_minutes:
        print(
            f"[log_run] estimate {args.estimate_minutes} min · "
            f"actual {duration / 60:.1f} min "
            f"({record['estimate_error_ratio']}×)"
        )
    if exit_code != 0:
        print(
            "[log_run] NON-ZERO EXIT — this run is not evidence for any claim.",
            file=sys.stderr,
        )
    elif not (run_dir / "metrics.json").exists():
        print(
            "[log_run] no metrics.json — write one with `log_run.py metrics` "
            "before citing this run.",
            file=sys.stderr,
        )
    return exit_code


# ---------------------------------------------------------------- metrics


def cmd_metrics(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        raise SystemExit(f"not a run directory: {run_dir}")
    metrics = load_json(run_dir / "metrics.json")
    if args.from_file:
        metrics.update(load_json(Path(args.from_file)))
    for pair in args.set or []:
        if "=" not in pair:
            raise SystemExit(f"--set expects key=value, got: {pair}")
        key, value = pair.split("=", 1)
        metrics[key] = coerce(value)
    dump_json(run_dir / "metrics.json", metrics)
    print(json.dumps(metrics, indent=2))

    missing = [k for k in ("seed", "eval_set") if k not in metrics]
    if missing:
        print(
            f"[log_run] missing {', '.join(missing)} — a metric without these "
            "cannot be compared across runs (conventions.md § metrics.json).",
            file=sys.stderr,
        )
    return 0


# ---------------------------------------------------------------- check


def cmd_check(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        raise SystemExit(f"not a run directory: {run_dir}")

    problems, warnings = [], []
    for required in REQUIRED_FOR_CITATION:
        if not (run_dir / required).exists():
            problems.append(f"missing {required}")

    try:
        record = load_json(run_dir / "run.json")
        metrics = load_json(run_dir / "metrics.json")
    except ValueError as exc:
        print(f"FAIL  {exc}")
        return 1
    if type(record.get("exit_code")) is not int or record["exit_code"] != 0:
        problems.append("run did not complete with integer exit_code 0")
    if not record.get("finished_at"):
        problems.append("no finished_at — run has not completed")
    git = record.get("git") if isinstance(record.get("git"), dict) else {}
    if git.get("dirty"):
        warnings.append("git tree was dirty at run time")
    if not git.get("sha"):
        warnings.append("no git SHA — provide another code snapshot before citing")
    if not metrics:
        problems.append("metrics.json is empty")
    for key in ("seed", "n_examples", "eval_set", "eval_set_sha256"):
        if key not in metrics or metrics[key] is None or metrics[key] == "":
            problems.append(f"metrics.json missing {key}; use an explicit not-applicable explanation for non-dataset runs")
    notes_path = run_dir / "notes.md"
    notes = notes_path.read_text() if notes_path.is_file() else ""
    if not notes.strip():
        problems.append("notes.md is empty")
    placeholders = ("<what this run", "<fill in after", "<which checks", "<what this does")
    if any(x in notes for x in placeholders):
        problems.append("notes.md is still the unfilled template")
    if "## Verification" not in notes:
        problems.append("notes.md has no Verification section")
    else:
        body = notes.split("## Verification", 1)[1].split("##", 1)[0].strip()
        if not body or body.startswith("<"):
            problems.append("notes.md Verification is empty — nothing was checked")

    for line in problems:
        print(f"FAIL  {line}")
    for line in warnings:
        print(f"WARN  {line}")
    if not problems:
        print(f"OK    {run_dir.name} passes structural checks; scientific validity requires review" + (" (with warnings)" if warnings else ""))
    return 1 if problems else 0


# ---------------------------------------------------------------- trajectory


def cmd_trajectory(args: argparse.Namespace) -> int:
    loop_dir = Path(args.loop_dir)
    loop_dir.mkdir(parents=True, exist_ok=True)
    path = loop_dir / "trajectory.json"
    rounds = load_json(path).get("rounds", []) if path.exists() else []

    if args.round < 0 or any(r["round"] >= args.round for r in rounds):
        raise ValueError("append rounds in increasing order; do not overwrite existing history")
    if any(not math.isfinite(x) for x in (args.primary, args.noise_floor, args.secondary, args.gpu_hours, args.dollars) if x is not None):
        raise ValueError("trajectory values must be finite")
    if any(x is not None and x < 0 for x in (args.noise_floor, args.gpu_hours, args.dollars, args.human_interventions)):
        raise ValueError("noise, costs, and intervention counts must be nonnegative")
    for constraint in args.constraint or []:
        if "=" not in constraint or constraint.split("=", 1)[1] not in ("pass", "fail"):
            raise ValueError("--constraint expects NAME=pass|fail")
    previous = rounds[-1] if rounds else None
    delta = (
        round(args.primary - previous["primary"], 6) if previous else None
    )
    cost_per_point = None
    if delta and delta > 0 and args.dollars is not None:
        cost_per_point = round(args.dollars / delta, 2)

    verdict = "baseline"
    if delta is not None:
        if args.noise_floor is None:
            # Without a noise floor a delta has no scale; refuse to call it either way.
            verdict = "uninterpretable — no noise floor measured"
        elif abs(delta) < args.noise_floor:
            verdict = "below noise floor — saturation candidate"
        elif delta < 0:
            verdict = "regression"
        else:
            verdict = "gain above noise floor"

    entry = {
        "round": args.round,
        "run_id": args.run_id,
        "parent_round": previous["round"] if previous else None,
        "recorded_at": now(),
        "primary": args.primary,
        "delta": delta,
        "noise_floor": args.noise_floor,
        "secondary": args.secondary,
        "cost": {"gpu_hours": args.gpu_hours, "dollars": args.dollars},
        "cost_per_point": cost_per_point,
        "human_interventions": args.human_interventions,
        "constraints": dict(
            c.split("=", 1) for c in (args.constraint or []) if "=" in c
        ),
        "verdict": verdict,
    }

    rounds = [r for r in rounds if r["round"] != args.round] + [entry]
    rounds.sort(key=lambda r: r["round"])
    dump_json(path, {"loop": loop_dir.name, "rounds": rounds})
    print(json.dumps(entry, indent=2))

    if args.noise_floor is None and args.round > 0:
        print(
            "[log_run] no --noise-floor — marginal gain is uninterpretable and "
            "saturation cannot be defined (driving-functions.md § The Noise "
            "Floor Comes First).",
            file=sys.stderr,
        )
    if args.human_interventions is None:
        print(
            "[log_run] no --human-interventions — this is the number that "
            "decides whether the loop is self-improving or a treadmill.",
            file=sys.stderr,
        )
    else:
        prior = [
            r["human_interventions"]
            for r in rounds
            if r["round"] < args.round and r.get("human_interventions") is not None
        ]
        if prior and args.human_interventions > prior[-1]:
            print(
                "[log_run] human-gate load ROSE this round. The loop is not "
                "self-improving. Surface this before reporting the score.",
                file=sys.stderr,
            )
    return 0


# ---------------------------------------------------------------- cli


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="log_run.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--results-dir", default=str(RESULTS_DIR),
        help=f"default: {RESULTS_DIR}",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run a command and log everything about it")
    p_run.add_argument("--name", required=True, help="kebab-case slug for the run")
    p_run.add_argument("--config", help="config file to copy into the run directory")
    p_run.add_argument("--estimate-minutes", type=float,
                       help="your pre-run estimate, for calibration")
    p_run.add_argument("--note", help="one line on why this run exists")
    p_run.add_argument("command", nargs=argparse.REMAINDER,
                       help="-- then the command to run")
    p_run.set_defaults(func=cmd_run)

    p_metrics = sub.add_parser("metrics", help="write or update metrics.json")
    p_metrics.add_argument("run_dir")
    p_metrics.add_argument("--set", action="append", metavar="KEY=VALUE")
    p_metrics.add_argument("--from-file", help="merge a JSON file of metrics")
    p_metrics.set_defaults(func=cmd_metrics)

    p_check = sub.add_parser("check", help="is this run citable in the journal?")
    p_check.add_argument("run_dir")
    p_check.set_defaults(func=cmd_check)

    p_traj = sub.add_parser("trajectory", help="append a round to a loop trajectory")
    p_traj.add_argument("loop_dir")
    p_traj.add_argument("--round", type=int, required=True)
    p_traj.add_argument("--run-id", required=True)
    p_traj.add_argument("--primary", type=float, required=True)
    p_traj.add_argument("--noise-floor", type=float)
    p_traj.add_argument("--secondary", type=float)
    p_traj.add_argument("--gpu-hours", type=float)
    p_traj.add_argument("--dollars", type=float)
    p_traj.add_argument("--human-interventions", type=int)
    p_traj.add_argument("--constraint", action="append", metavar="NAME=pass|fail")
    p_traj.set_defaults(func=cmd_trajectory)

    args = parser.parse_args()
    if args.cmd == "run":
        if args.command and args.command[0] == "--":
            args.command = args.command[1:]
        if not args.command:
            parser.error("no command given — put it after `--`")
    try:
        return args.func(args)
    except (ValueError, OSError) as exc:
        print(f"[log_run] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
