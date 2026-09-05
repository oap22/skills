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
diskutil info "$DRIVE" | grep -Ei "file system|read-only"
```

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

## Pre-archive checks for a repo

1. Confirm it is pushed. Unpushed commits exist only in that working tree:
   ```bash
   git -C <repo> status
   git -C <repo> log origin/HEAD..HEAD
   ```
   Any output from the second command means local-only history. Stop and tell
   the user.

2. Move whole repos including `.git`. An extract without history is not an
   archive.

3. Use `rsync` over `mv` for large trees so an interrupted transfer resumes:
   ```bash
   rsync -a <repo>/ "$DRIVE/Archive/Developer/<name>/"
   ```

4. Verify the destination before removing the source:
   ```bash
   git -C "$DRIVE/Archive/Developer/<name>" status
   ```
   Also compare source and destination with a checksum dry run (`rsync -acn --itemize-changes`), inspect file modes/symlinks, run `git fsck`, and compare refs plus dirty/untracked files. Keep the source until verification passes and source removal is explicitly authorized. Linked worktrees reference Git data outside their directory; archive the owning repository or materialize a standalone copy first.

## Triaging which repos are dormant

Sort by last commit date rather than guessing from names:

```bash
for d in ~/Developer/*/; do
  [ -d "$d/.git" ] && printf "%s\t%s\n" \
    "$(git -C "$d" log -1 --format=%cs 2>/dev/null)" "$d"
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
