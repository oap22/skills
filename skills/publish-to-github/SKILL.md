---
name: publish-to-github
description: Put a local directory under version control and push it to a new private GitHub repo, scanning for secrets and excluding regenerable machine state first. Use when the user says "push this to GitHub", "put this under version control", "make a private repo for this", "back this up", or when a directory holding real work has no git remote.
---

# Publish to GitHub

Get unbacked work off a single disk, without publishing secrets or committing gigabytes of regenerable state.

Pairs with `project-sync`, which flags local repos that have no remote — this is the fix for what it finds.

## Steps

### 1. Check what already exists

```bash
test -d .git && echo "already a repo" || echo "no version control"
git remote -v 2>/dev/null
gh auth status
```

If it's already a repo with a remote, stop — there's nothing to do. If it's a repo with no remote, skip to step 5.

### 2. Find the bulk

Most directories are mostly machine state. Measure before deciding what to ignore:

```bash
du -sh ./* ./.* 2>/dev/null | sort -rh | head -12
find . -type f -size +2M -not -path "./.git/*" 2>/dev/null | head
```

Sort what you find into **work** (source, notes, configs worth keeping) and **regenerable state** (caches, indexes, embeddings, build output, vendored binaries, virtualenvs). The ratio is often extreme — an Obsidian vault measured at 101 MB held 1.5 MB of actual notes; the rest was plugin binaries and search indexes.

Report the split. It's usually surprising and it justifies the `.gitignore`.

### 3. Write the .gitignore

Exclude everything regenerable, and be specific rather than sweeping — ignoring a whole config directory usually throws away settings worth versioning alongside the binaries that aren't.

Always exclude, regardless of project type:

```gitignore
**/*.local.json
**/*.local.sh
.DS_Store
**/.DS_Store
```

### 4. Scan for secrets — do not skip

A private repo is still a copy on someone else's servers, and history is permanent once pushed.

```bash
grep -rlniE 'bearer [a-z0-9]|api[_-]?key["'"'"': ]+[a-z0-9]{12}|token["'"'"': ]+[a-z0-9]{16}|password|BEGIN [A-Z ]*PRIVATE KEY' . --include="*.md" --include="*.json" --include="*.sh" --include="*.yml" --include="*.env*" 2>/dev/null
```

**Then open every match and read the actual value.** The filename-level hit rate is mostly false positives — prose containing the word "password", or config templates. What matters is whether the value is real:

- `"Bearer PASTE_KEY_FROM_PLUGIN"` — placeholder, safe
- `ssh-ed25519 AAAA...` — a **public** key, safe by design
- `BEGIN OPENSSH PRIVATE KEY` — stop, never commit
- A long random-looking string in a config file — treat as real until proven otherwise

If a real credential is found, add it to `.gitignore`, remove it from the working tree, and confirm it isn't already in git history before pushing.

### 5. Stage and verify before committing

```bash
git add -A
git diff --cached --name-only | wc -l
git diff --cached --name-only | while read -r f; do
  [ -f "$f" ] && s=$(stat -f%z "$f" 2>/dev/null) && [ "$s" -gt 1000000 ] && echo "$f"
done
```

Anything over ~1 MB staged means the `.gitignore` missed something. Fix it before the commit, not after — large files in history are painful to remove.

### 6. Commit and create

```bash
git init -q
git commit -m "<message>"
gh repo create <name> --private --source=. --remote=origin --push
```

### 7. Verify visibility — always

Never assume the flag worked:

```bash
gh repo view <owner>/<name> --json name,visibility,url,pushedAt
```

Confirm `"visibility":"PRIVATE"` and report the URL.

## Rules

- **Default to private.** Only create a public repo when the user explicitly asks.
- **Never commit a private key, real token, or `.env` with live values.**
- **Say what's now on GitHub.** If the content includes personal information — finances, health, grades, names of family — tell the user plainly that it left the machine, even into a private repo.
- **Don't rewrite history** to remove a secret without asking; that's a destructive operation with its own risks.
- **Don't add a remote to a repo that already has one** without confirming.

## Environment

- **`ls` is aliased to a git-aware tool that hangs for minutes in a fresh repo.** Immediately after `git init`, use `/bin/ls`. This has caused a real 2-minute timeout.
- **zsh aborts on non-matching globs** — use `find | while read` for file loops.
- macOS `stat` takes `-f%z`, not GNU's `-c%s`.
