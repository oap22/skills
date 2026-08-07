---
name: project-sync
description: Scan local git repos and sync them into the Obsidian vault as project notes, with an inventory table and flags for unbacked or duplicated work. Use when the user says "sync my projects", "update my project notes", "scan my repos", "what am I working on", or wants the vault's 02-Projects to match what's actually on disk.
---

# Project Sync

Reconcile `~/Developer` (and anywhere else repos live) against `02-Projects/` in the vault. Repos change constantly and the vault goes stale silently — this closes the gap.

**Vault:** `/Users/owenpacetti/Owen's Awesome Vault`
Read `.system/frontmatter-schema.md` and `.system/agent-conventions.md` before writing anything.

## Steps

### 1. Discover

```bash
find ~ -maxdepth 4 -name ".git" -type d \
  -not -path "*/node_modules/*" -not -path "*/.Trash/*" -not -path "*/Library/*" \
  2>/dev/null | sed 's|/.git$||'
```

Depth 4 catches nested groupings like `research-group-26-27/<repo>`. Raise it if repos are buried deeper. Note that agent tool directories (`~/.codex`, `~/.claude`) contain git repos — exclude them.

### 2. Collect metadata

Per repo: last commit date (`git log -1 --format=%cs`), commit count (`git rev-list --count HEAD`), current branch, and origin remote shortened to `owner/name`.

Then read the first few lines of `README.md`, stripping HTML tags and badge lines, and detect the build file (`package.json`, `Cargo.toml`, `pyproject.toml`, `requirements.txt`, `go.mod`, `CMakeLists.txt`, `Makefile`, `index.html`).

**The README is the only thing that tells you what a repo actually is.** Never write a project note from the directory name alone — you will guess wrong.

### 3. Triage

Not every repo earns a note. Same principle as inbox triage: the vault should be dense, not complete.

| Repo | Action |
|---|---|
| Real work — commits, a README, an outcome | **Write a note** |
| Tutorial follow-along, zero commits (`hello_cargo`, book exercises) | Index row only |
| Upstream clone under someone else's org | Index row only, noted as upstream |
| Duplicate copy of another repo | Index row only, flagged |

Check the remote's **owner** to tell your own work from a clone. A repo whose origin points at another user's account is someone else's codebase you're working in — file it as research, not as a personal build.

### 4. Write notes

One note per project at `02-Projects/<Title-Case-Hyphenated>.md`, matching the vault schema:

```yaml
---
tags:
  - project
  - <domain-tags>
type: personal          # personal | school | research
status: active          # active | paused | done
date: <today>
last-commit: YYYY-MM-DD
repo: <origin URL, omit if none>
moc: "[[01-Maps/MOC - ...]]"
---
```

Body: what it is (from the README, in your own words), status with commit count and branch, stack, why it matters, and `## See Also` wikilinks to related projects and MOCs.

Infer `status` from recency — roughly: within ~2 months `active`, older `paused`, finished efforts `done`. **Say in the report that status was inferred**, so wrong guesses get corrected rather than silently trusted.

### 5. Build the inventory

Add or update a table in `02-Projects/README.md`: every project with type, status, commit count, and last commit, sorted by status then activity. Include a separate section for repos that got no note, with the reason.

### 6. Flag what's wrong

The point of the sweep. Surface, don't fix:

- **No git remote** — work existing only on this machine, one disk failure from gone.
- **Crossed or contradictory READMEs** — a rename that never finished. Two repos claiming each other's names.
- **The same project in multiple directories.**
- **Stale branches** — substantial work sitting on a non-default branch.

Report these prominently. They are usually things the user does not know are true.

### 7. Report

Notes created vs updated, the inventory location, every flag, and an explicit note that statuses were inferred from commit dates.

## Rules

- **Never delete a project note.** Vault rule. If a repo disappeared, mark the note `status: done` or move it to `04-Archives/` — ask first.
- **Prefer updating over rewriting.** Notes accumulate hand-written context; a sync must not flatten it. Refresh frontmatter and status, leave prose alone.
- **Wikilinks only**, never markdown links, per vault conventions.
- **Wikilinks must resolve to a note, not a folder.** `[[Personal/Research/Graphics and Rendering]]` is a broken link; point at a note inside it.
- **Don't invent descriptions.** No README and no clear purpose means the note says so.

## Environment gotchas

These cost real time on this machine.

- **zsh does not word-split unquoted variables.** `for s in $LIST` iterates *once* with the whole string. Use a literal list in the `for`, or a proper array. This silently produces a near-empty result rather than an error — a backup loop written this way copied 1 of 27 files and still exited 0.
- **`ls` is aliased to a git-aware tool that hangs** for minutes inside a fresh or large git repo. Use `/bin/ls` in scripts.
- **macOS ships bash 3.2** — no associative arrays, no `mapfile`. For anything involving JSON or key-value maps, write Python instead of fighting it.
- Verify loop output counts before acting on the result. A loop that "succeeded" but processed one item looks identical to success.
