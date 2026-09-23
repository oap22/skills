---
name: reclaim-disk-space
description: "Free space on a Mac: survey where the disk went, delete regenerable caches, archive dormant files to a verified external drive. Use for \"my mac is full\", \"free up storage\", or \"move my files to my external drive\"."
---

# Reclaim Disk Space

Survey first, delete by tier, archive last. The user's theory about where the
space went is usually wrong — measure before you move anything.

## Steps

### 1. Survey before believing the premise

Never act on the stated cause. Measure all four regions — space is routinely
outside the home directory:

```bash
df -h | grep -v "^map"
du -sh ~/* ~/.[!.]* 2>/dev/null | sort -rh | head -25
du -sh ~/Library/* 2>/dev/null | sort -rh | head -15
du -sh /Applications /Library /opt /usr/local 2>/dev/null | sort -rh
```

**The `~/.[!.]*` glob is not optional.** A bare `~/*` skips every dotfile, and
that is where model stores and language caches live — `~/.ollama/models` alone
was 46 GB on a machine where the whole survey had reported nothing bigger than
`~/Library` (observed 2026-08-12; caught only when the user asked an unrelated
Ollama question). Also check `~/.cache`, `~/.cargo`, `~/.rustup`, `~/.npm`,
`~/.gradle`, `~/.pyenv`, `~/.docker`, `~/.lmstudio`.

If the home total is far below the Data volume's used figure, the difference is
in `/Applications`, `/Library`, and `/opt` (observed 2026-08-12: home 123 GB
against 388 GB used; `/Applications` 36 GB, `/Library` 26 GB, `/opt` 18 GB,
all invisible to `du -sh ~/*`). Drill into the largest hits with
`du -sh <dir>/*` until you reach actual files.

Report the real numbers before proposing anything. If the folders the user named
turn out to be trivial, say so plainly with the sizes (observed 2026-08-12:
"migrate my documents to save space" — Documents 16 MB, Downloads 12 KB, Desktop
empty; the 83 GB was Docker and caches).

### 2. Classify every candidate into one of three tiers

| Tier | Meaning | Action |
|---|---|---|
| **1 — Regenerable** | Rebuilds itself on demand, no state lost | Delete, just report it |
| **2 — Rebuildable state** | Re-creatable but destroys real work | Explicit confirmation, item by item |
| **3 — Real data** | Only copy in existence | Never delete. Archive or leave |

Tier 1 — package caches (`~/Library/Caches/{Homebrew,pip,npm,node-gyp}`),
browser caches (`Google`, `Arc`, `BraveSoftware`), `electron`, `ms-playwright`,
wallpaper aerials (`~/Library/Application Support/com.apple.wallpaper/aerials`),
Electron app `Cache`/`Code Cache` subdirectories, **and confirmed re-downloadable model
weights** — `~/.ollama/models`, LM Studio, Hugging Face caches. A model that
`ollama pull` restores is regenerable, not data. Delete the stale ones; never
archive them to a drive.

`ollama list` modification times do not prove last use. Check the active process, user context, and model provenance. Custom/imported/fine-tuned weights may be the only copy and belong in Tier 3. Remove only confirmed re-downloadable, unused models within the authorized cleanup scope, using the model manager rather than deleting its entire store.

Tier 2 — Docker's VM image, iOS simulator runtimes, Xcode `DerivedData`,
sandbox VM bundles. Each destroys something. Name what is lost, per item.

Tier 3 — anything else. Archiving is a *move plus verify*, never a delete.

### 3. Confirm the Tier 2 items individually

State for each: bytes reclaimed, what is destroyed, and how to get it back. Get
an explicit yes. Do not bundle them into one approval — the user may want the
50 GB Docker image gone and the simulator kept.

If the harness has a structured question tool, use it to present the tiers.
Otherwise ask in prose and wait.

### 4. Delete, measuring as you go

Capture free space before and after so the report is measured, not estimated:

```bash
before=$(df -k / | awk 'NR==2{print $4}')
# ... deletions ...
after=$(df -k / | awk 'NR==2{print $4}')
echo "reclaimed: $(( (after-before)/1024/1024 )) GB"
```

### 5. Only now consider the external drive

Most sessions end here without ever touching it. Archive only when Tier 1 and 2
are exhausted and real data still needs to move. See
[external-drive-layout.md](external-drive-layout.md) for the drive structure,
formatting procedure, and pre-archive checks.

### 6. Report

Before/after free space, a table of what was deleted with sizes, anything that
needed `sudo` (give the user the command), and anything deliberately left alone
with the reason.

## Rules

**`du` lies about sparse files, `ls -lh` lies harder.** Docker's `Docker.raw`
reports a 494 GB apparent size and 50 GB on disk. Trust `du -sh`, never `ls -lh`,
and say "on-disk" in the report so the number isn't disputed.

**`du` on `/Library/Developer/CoreSimulator` counts mounted volume contents,
not the backing image.** It reported 19 GB where the real reclaim was 7.9 GB.
Get true sizes from `xcrun simctl runtime list`.

**Delete simulator runtimes through `simctl`, not `rm`.** The directory is
root-owned and `rm` leaves the runtime registered:

```bash
xcrun simctl shutdown all
xcrun simctl delete unavailable
xcrun simctl runtime delete <UUID>
```

Deletion is asynchronous — the runtime sits in `Deleting` state. Poll
`xcrun simctl runtime list` until the count drops before reporting the space.

**Check whether Docker is running before removing its image.** `pgrep -fl
"Docker Desktop|com.docker"` — `com.docker.vmnetd` alone is just the privileged
helper daemon and is safe. Deleting `Docker.raw` wipes every image, container,
and named volume; Docker.app survives and builds a fresh empty VM.

**Root-owned directories need the user's password.** Don't attempt `sudo` —
surface the exact command and let them run it.

**Never archive an active notes vault, or anything synced.** Obsidian vaults,
iCloud Drive, OneDrive. Moving these to an external breaks sync and makes the
user's daily work depend on a cable.

**Check for empty sync folders while surveying.** A 0-byte `~/OneDrive - <org>`
or similar means sync isn't running and that content isn't on the machine at
all — worth flagging even though it's unrelated to space.

**Re-resolve the mount path before every drive operation.** Volume names change
— a user renaming the drive in Finder moves it from `/Volumes/Elements` to
`/Volumes/External-Drive` mid-session. Never cache the path; check `ls /Volumes`
or `diskutil list external` each time.

**Benchmark the drive before recommending offload, and only when it informs
the requested storage decision.** Read speed, not write speed, decides whether
a drive can hold working data. Procedure and thresholds:
[external-drive-layout.md](external-drive-layout.md) § Benchmark.
