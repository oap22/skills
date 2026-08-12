---
name: reclaim-disk-space
description: Free up space on a Mac by surveying where the disk actually went, then deleting regenerable caches and archiving dormant files to an external drive. Use when the user says "my mac is full", "running out of space", "free up storage", "clean up my disk", "move my files to my external drive", "startup disk is almost full", or wants to migrate documents off the machine to save space.
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
du -sh ~/* 2>/dev/null | sort -rh | head -20
du -sh ~/Library/* 2>/dev/null | sort -rh | head -15
du -sh /Applications /Library /opt /usr/local 2>/dev/null | sort -rh
```

If the home total is far below the Data volume's used figure, the difference is
in `/Applications`, `/Library`, and `/opt`. Drill into the largest hits with
`du -sh <dir>/*` until you reach actual files.

Report the real numbers before proposing anything. If the folders the user named
turn out to be trivial, say so plainly with the sizes.

### 2. Classify every candidate into one of three tiers

| Tier | Meaning | Action |
|---|---|---|
| **1 — Regenerable** | Rebuilds itself on demand, no state lost | Delete, just report it |
| **2 — Rebuildable state** | Re-creatable but destroys real work | Explicit confirmation, item by item |
| **3 — Real data** | Only copy in existence | Never delete. Archive or leave |

Tier 1 — package caches (`~/Library/Caches/{Homebrew,pip,npm,node-gyp}`),
browser caches (`Google`, `Arc`, `BraveSoftware`), `electron`, `ms-playwright`,
wallpaper aerials (`~/Library/Application Support/com.apple.wallpaper/aerials`),
Electron app `Cache`/`Code Cache` subdirectories.

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

## Failure modes seen

- **Acting on the stated premise.** Session opened with "migrate my documents to
  save space." Documents was 16 MB; Downloads 12 KB; Desktop empty. The 83 GB
  came from Docker and caches. Surveying first is the entire skill.
- **Assuming the home directory is the disk.** Home was 123 GB against 388 GB
  used. `/Applications` (36 GB), `/Library` (26 GB), and `/opt` (18 GB) were
  invisible to `du -sh ~/*`.
- **Reformatting without verifying the device.** Always confirm `external,
  physical`, the media name, and the size via `diskutil info <disk>` and check
  it against the internal disk identifier before any erase.
