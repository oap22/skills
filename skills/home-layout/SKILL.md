---
name: home-layout
description: "Place, move, rename, or archive project and document folders in Owen's home directory under the ~/code layout, with unique names, a move log, and old-path repair. Use for \"where does this project go\", \"reorganize my folders\", \"archive this repo\", \"I have duplicate folders\". Disk-space cleanup is reclaim-disk-space."
---

# Home Layout

One home for each project. Each folder name is unique. Every move is logged, and every old path is repaired.

## Layout

```
~/code/
  me/<repo>        personal projects and tools
  res/<repo>       research, school-affiliated or personal
  org/<name>       clubs and organizations (AI Club, MAIC, hackathon teams), code or not
  sch/<course>/    one folder per course code, lowercase (csc2210/); repos and course files go inside
  tmp/             scratch; anything here can be deleted
~/life/            personal non-code: career, speeches, resume reviews, channel material
~/ref/             papers, reading, wallpapers
~/arc/             all archives, flat, named <ctx>-<name> (sch-csc1110, me-fractals, org-maic)
~/vault            symlink to the Obsidian vault (its real name has spaces)
```

Apps own `~/Claude`, `~/Documents/Claude`, and `~/Documents/Codex`. Do not move them by hand.
`~/Desktop` and `~/Downloads` stay empty. `~/FILE-ORGANIZATION.md` records the current state and the exceptions (paths that tools hardcode).

## Rules

1. **Context comes from who the work is for.** Course work goes in `sch`, research in `res`, clubs in `org`, and everything else in `me`. If a project fits two contexts, ask Owen once.
2. **A name exists once.** Before you make a folder, run `python3 find_dupes.py` (in this skill directory) and `zoxide query -l <name>`. If the name exists, use that folder, or pick a more specific name. The check is case-insensitive because macOS treats `School` and `school` as the same folder.
3. **Do not nest a folder inside one with the same name** (`Speeches/speeches`, `skills/skills` in a new project).
4. **Keep the repo folder name.** Shorten parent folders, not repos. A renamed repo breaks every hardcoded path.
5. **Fixed depth.** Repos are at `~/code/<ctx>/<repo>`, or at `~/code/sch/<course>/<repo>` for school.
6. **Archive flat.** To archive, move the folder to `~/arc/<ctx>-<name>`. To bring it back, move it back. Nothing else changes.
7. **Deletion is not part of a move.** Delete only items that Owen approves one at a time. Before you delete a repo, see [Delete check](#delete-check).

## Steps for a move

1. Read `~/FILE-ORGANIZATION.md`.
2. Write the plan as rows of `action<TAB>from<TAB>to`. Show it to Owen if it has more than five rows or touches a repo with linked worktrees.
3. Append each row to `~/code/.reorg-log-<YYYY-MM>.tsv` **before** you move. An unlogged move had to be reconstructed by hand in September 2026.
4. Move with `mv` on the same volume. In a repo that has linked worktrees, run `git worktree repair` after the move. Move a linked worktree with `git worktree move`, not `mv`.
5. Repair the old paths. Run `grep -rIl --exclude-dir=node_modules -- "<old path>"` over:
   - the agent instruction files and configs (`~/.claude`, `~/.codex`, Cursor, OpenCode, Copilot). Regenerate them with the agent-system setup script, not by hand.
   - Codex trusted-project paths in `~/.codex/config.toml`
   - the skills repo, then `python3 install.py --check` and `python3 install.py`
   - scheduled tasks in `~/.claude/scheduled-tasks/`
   - the living docs in the vault. Do not change dated records (logs, journals, run outputs, audits).
6. Update zoxide: `zoxide add <new>` and `zoxide remove <old>`.
7. Update `~/FILE-ORGANIZATION.md`.

## Verify

- `python3 find_dupes.py` prints nothing.
- The grep for each old path finds only dated records.
- `git -C <repo> status` works for each moved repo and each linked worktree. Run this on the Mac (see Gotchas).
- `python3 install.py --check` passes in the skills repo.

## Delete check

For each repo that is a delete candidate, get these facts and show them to Owen as a table:

```bash
git -C <repo> fetch --all --prune      # the remote refs can be old
git -C <repo> remote -v                # no remote means this is the only copy
git -C <repo> status --porcelain       # files not yet committed
git -C <repo> log --branches --not --remotes --oneline   # commits not pushed
git -C <repo> stash list
git -C <repo> worktree list
```

A repo is safe to delete only if it has a remote, no unpushed commits, no uncommitted files, no stash, and no linked worktrees. If not, give the options: push and then delete, archive it, or keep it. Build output (`node_modules`, `.venv`, `target`, `.mypy_cache`) can be rebuilt. For that, use reclaim-disk-space.

## Gotchas

- **Linked worktrees fail from a mounted copy of the home folder.** On 2026-10-07, git in the desktop-workspace VM said "not a git repository" for `t3code-dev` and for every Turing `.worktrees/*`. The `.git` file in a worktree holds an absolute Mac path. Run worktree checks on the Mac. If you cannot, report the status as unknown.
- **Stray folders come back after a move.** The September 2026 tidy merged `~/Developer/galaxy-cluster-research`. On 2026-09-29, the folder was back with only an `AGENTS.md`, so something still wrote to the old path. The cause is not known. Run `find_dupes.py` again a few days after a move.
- **"Unpushed" counts without a fetch can be wrong.** On 2026-10-07, most repos showed 1 unpushed commit with the same 2026-09-21 date. Fetch before you use this count to decide on a delete.
- **Some tools hardcode their paths.** Turing writes to `~/research-results` and `~/turing-workspace` (checked 2026-09-17). Leave these folders in place, or change the tool first.
- **A broad move breaks many links at once.** The September 2026 nesting left 112 dangling skill symlinks and stale agent configs, worktrees, scheduled tasks, and Codex trust paths. Do step 5 for every move, not only for large moves.
