# External Drive Layout

Read this only when archiving is actually needed. Most cleanup sessions finish
without touching the external drive.

## Standard structure

```
Archive/
  Developer/    Dormant git repos. Full working tree, .git included.
  Documents/    Finished documents no longer in active rotation.
  Media/        Photos, video, large binaries.
Backups/        Time Machine target, or manual snapshots.
Scratch/        Transient large files. Anything here is disposable.
README.md       What goes where, and why.
```

Create it on a fresh drive with:

```bash
cd "$DRIVE" && mkdir -p Archive/Developer Archive/Documents Archive/Media Backups Scratch
```

Write a `README.md` at the root recording the format, the date, and these rules.
A drive with no README becomes an undifferentiated dumping ground within a term.

## Format check — do this before archiving anything

```bash
diskutil info "$DRIVE" | grep -Ei "file system|read-only|device location|free space"
```

Set `DRIVE` from `diskutil list external`; never default it. Stop if the output says `Could not find disk` (not mounted: ask the user to connect it), says `Device Location: Internal`, or shows less free space than the archive needs.

**exFAT cannot safely hold git repos.** No symlinks, no Unix permissions, and
case-insensitive in a way that silently collides filenames. It corrupts
`node_modules` and loses file modes on checkout. Most drives ship exFAT from the
factory and stay that way for years.

For exFAT, offer a verified archive file that preserves links and modes, or an APFS destination. Reformatting is optional and destructive; inventory the entire device and obtain explicit erase authorization before using it.

## Reformatting

Verify the device first. Confirm `external, physical`, the media name, and the
size, and check the identifier is not the internal disk:

```bash
diskutil list external
diskutil info <verified-external-disk-id> | grep -Ei "device identifier|media name|internal|virtual|disk size"
```

Then:

```bash
diskutil unmountDisk <verified-external-disk-id>
diskutil eraseDisk APFS <VolumeName> GPT <verified-external-disk-id>
```

**Choose case-insensitive APFS**, the default. It matches the internal macOS
volume, so trees move in both directions without filename collisions. Case-
sensitive APFS is more faithful to Linux but creates collisions on the return
trip, which is the direction that loses data.

## Benchmark before offloading working data

Confirm free space, use a unique scratch file, and do not unmount a drive with
active applications or transfers. Write speed does not predict read speed on
USB enclosures — one drive benchmarked at 284 MB/s write and 92 MB/s read, a 3×
gap (observed 2026-08-12, after offload had already been recommended; the
advice had to be walked back). Working storage is read-bound, so the write
figure flatters it badly:

```bash
BENCH_FILE=$(mktemp "$DRIVE/.skills-bench.XXXXXX")
dd if=/dev/zero of="$BENCH_FILE" bs=1m count=4000 conv=fsync   # write
diskutil unmount "$DRIVE" && diskutil mount <volume>          # drop cache
dd if="$BENCH_FILE" of=/dev/null bs=1m                         # cold read
rm -f "$BENCH_FILE"
```

Use `conv=fsync` or the write number is buffered and inflated, and remount
before reading or the read number is page cache (it will show absurd GB/s).
Check `mdutil -s "$DRIVE"` first — Spotlight indexing a freshly mounted volume
corrupts the measurement.

Below ~200 MB/s read, the drive is cold storage only. Memory-mapped workloads —
Ollama, LM Studio, anything faulting pages during use — stall rather than slow
when the mapping lives on a slow external.

## Pre-archive checks for a repo

1. Confirm it is pushed. Unpushed commits exist only in that working tree:
   ```bash
   git -C <repo> status --porcelain
   git -C <repo> log --branches --not --remotes --oneline
   git -C <repo> stash list
   ```
   Any output means work that exists only here. Stop and tell the user. Do not
   use `origin/HEAD..HEAD`: it errors when `origin/HEAD` is unset and checks one
   branch (observed 2026-10-05).

2. Move whole repos including `.git`. An extract without history is not an
   archive.

3. Copy, never `mv`, so the source survives until verification:
   ```bash
   ditto <repo> "$DRIVE/Archive/Developer/<name>"   # keeps xattrs, ACLs, hard links
   ```
   macOS `/usr/bin/rsync` is openrsync (since 15.4): plain `rsync -a` drops
   xattrs and hard links, and `-X` is rejected.

4. Verify the destination before removing the source:
   ```bash
   git -C "$DRIVE/Archive/Developer/<name>" status
   ```
   Also compare source and destination with a checksum dry run (`rsync -acn --itemize-changes`), inspect file modes/symlinks, run `git fsck`, and compare refs plus dirty/untracked files. Keep the source until verification passes and source removal is explicitly authorized. Linked worktrees reference Git data outside their directory; archive the owning repository or materialize a standalone copy first.

## Triaging which repos are dormant

Sort by last commit date rather than guessing from names:

```bash
find ~/Developer -maxdepth 4 -name .git -prune 2>/dev/null | while read -r g; do
  r=${g%/.git}; printf "%s\t%s\n" "$(git -C "$r" log -1 --format=%cs 2>/dev/null)" "$r"
done | sort
```

Present the sorted list and let the user pick. Do not infer dormancy from a
throwaway-sounding name — tutorial repos sometimes hold the only copy of
coursework.

## Ejecting

```bash
diskutil eject "$DRIVE"
```

APFS is not journaled the way HFS+ was. Treat unplanned removal as a real
hazard, and eject explicitly at the end of any archiving session.
