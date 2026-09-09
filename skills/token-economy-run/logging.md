# Recording the run

Record once per task, at the point the task reaches `pass`, `fail`, or `partial` against its acceptance criteria. Not per packet, not per session restart.

```sh
python3 scripts/oas.py log-run --output /abs/workspace/.oas \
  --task <task id or short title> --harness claude --mode development --result pass \
  --lead-effort xhigh --worker-model sonnet --worker-effort low --retry-effort medium \
  --packets 3 --escalated 1 --cost-usd 1.42 --minutes 18 --corrections 0
python3 scripts/oas.py report-runs --output /abs/workspace/.oas
```

## Where each number comes from

- `--cost-usd`: what the harness reports for the session, subagents included. In Claude Code interactive sessions the figure is under `/usage`; `--max-budget-usd` counts subagent spend but applies to print mode only. Omit the flag when no figure is available; do not estimate.
- `--minutes`: wall clock from launch to result, if known.
- `--packets`, `--escalated`: from the session, per `escalation.md`.
- `--corrections`: substantive corrections Owen had to make to the delivered work. A faster wrong answer is a failure, and this column is where it shows.
- `--lead-model`: only when `--model` was passed at launch; omitted means the harness default was inherited.

## Reading the report

`report-runs` groups by configuration and prints cost per completed task: every dollar spent under that configuration, failed runs included, divided by the tasks it completed. Compare the split against the lead alone at `medium` and `high` on the same task type. If the split loses on a task type, stop delegating that type and say so. Token counts alone do not decide; a critical boundary failure (lost work, false completion, unauthorized action) blocks a configuration regardless of cost.

The log lives at `.oas/evals/runs.jsonl` in the workspace and is ignored by git. It contains model aliases and costs, which is why it never goes into a repository.
