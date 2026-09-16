# Ship

Read this before creating a branch or touching git. Review must already be clean and tests green before § Commit, except that a cloud implementer may already have committed on the feature branch — then skip to § PR.

## Branch — before the implementer runs

Do this **after spec approval, before spawn**. Implementation on `main`/`master` is how this skill pushes the default branch.

```bash
git branch --show-current
git status --short
git remote get-url origin
git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || true
```

1. **Dirty tree.** Preserve unrelated modified, staged, and untracked work. Create an isolated worktree when that avoids a conflict; do not make an otherwise unrelated dirty file a blocker. If authorized edits overlap existing work, inspect and preserve that diff before choosing an approach. (A cloud implementer clones clean; this check still protects the parent tree you will fetch back into.)
2. **Default branch.** Discover the actual default branch from the remote. Create a feature branch following the repository convention (`codex/<slug>` in Codex), or reuse the branch explicitly assigned to this task. Do not assume any non-main branch belongs to this work. Never commit to `main`/`master`. Never `git push` to `main`/`master`. Tell a cloud implementer this same branch name and the default-branch name it must branch from.
3. **Origin.** All `gh` and `git push` commands use **`origin` only**. Parse owner/name from `git remote get-url origin` (SSH or HTTPS). Pass that repo to `gh repo view` / `gh api` / `gh pr create`. Do not call `gh` without a repo argument and hope it matches `origin`.

## After a cloud or isolated implementer

The spec is gitignored, so that agent worked from the prompt copy. Bring its branch here before review:

```bash
git fetch origin "<branch>"
git checkout "<branch>"
```

If fetch fails, the isolated run did not push — stop and report. Do not review an empty local tree and call it their work. Repair loops spawn again onto **that same branch**.

## Permission check — before commit/push

```bash
gh repo view "$(git remote get-url origin)" --json owner,name,viewerPermission
```

Check both user authorization and actual repository rules. `viewerPermission` alone does not determine merge eligibility; WRITE may allow merge, and ADMIN does not waive required reviews. Existing collaborators do not prevent preparing a PR.

| `viewerPermission` | What you do |
|---|---|
| `ADMIN` or `MAINTAIN` | Push, open PR, request reviewers, merge after CI green (or no checks). |
| `WRITE` | Push and open PR when authorized; merge only if requested and permitted by the live rules and review/check state. |
| anything else | Stop. Diff is ready. Do not push. |

## Commit

If the cloud implementer already committed the Touch/Tests files on the feature branch, do not commit again unless review required repairs that landed locally.

Otherwise: named files only. Never `git add -A`. Never commit `.plan-then-ship/`. Never commit secrets. Never skip hooks. Never force-push.

Allowed named files: the spec's Touch list, the spec's Tests paths, and `.gitignore` if this run added `.plan-then-ship/` to it.

## PR

Message and PR title/body come from the spec. Create the PR against the repo's default branch from the current feature branch:

```bash
git push -u origin HEAD
gh pr create --repo "<owner>/<name>" --title "..." --body-file <description-file>
```

**Use the people on the repo.** If `CODEOWNERS` or `.github/CODEOWNERS` names users or teams, add them as reviewers. If there is no CODEOWNERS file, use the repository's review convention or an explicitly requested reviewer; do not notify every collaborator by default. A PR that notifies nobody on a multi-person repo is the failure mode.

## CI then merge

Waiting is not passing.

```bash
gh pr checks --watch
```

- **No checks:** eligible to merge (permission table above).
- **Every check succeeded:** eligible to merge.
- **Any check failed, cancelled, timed out, or still pending after watch:** **do not merge.** Stop and report the failing checks.

Then, only if eligible **and** merging is authorized and permitted by the current repository rules: merge. Prefer squash when the repo allows it (`gh pr merge --squash`).

If GitHub refuses because reviews are required, branch protection, or a collaborator must approve: **stop with the PR URL**. That is the multi-person workflow working. Do not override, do not `--admin` merge.

## `.gitignore`

Adding `.plan-then-ship/` to `.gitignore` is planner work, not implementer work. It is exempt from spec-fidelity "extra file" criticals. If it changed, it ships in the named-files commit above. The spec itself stays untracked — cloud agents get the spec in the prompt instead.
