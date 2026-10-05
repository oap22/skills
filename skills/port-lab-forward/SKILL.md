---
name: port-lab-forward
description: "Carry Owen's finished coursework from an old course repo into the fresh starter repo for the next lab: find the real source, diff against the starter, verify dependencies, copy only what was asked. Use for \"port my lab forward\", \"copy X from my old repo into the new one\", or \"my professor gave us a new repo\"."
---

# Port Lab Forward

Incremental courses hand out a new starter repo per checkpoint. Your finished work
from the last one has to move into it — but the starter is not empty, and it is not
frozen. Diff before you overwrite.

Not this skill: if the user wants help *writing* the lab, that is `professor` (which
refuses to write it for them). This skill only moves code the user already finished.
If the blocker is JDK/JavaFX/IntelliJ config rather than files, that is
`swe2410-java-setup`.

## Steps

1. **Locate both repos.** List the course directory. The starter is usually named for
   the term and checkpoint (`27s1-<course>-chk26-<user>`); the old one is the prior
   project or a personal course repo. If the old repo is not on disk, ask for its URL
   and clone it beside the starter; never rebuild the work from memory. Check
   `git status --short` and `git log --all --oneline -5` there, because the finished
   work can be uncommitted or on another branch. In the starter, `git fetch` and pull
   if it is behind and clean, so the diff runs against its current state.

2. **Find the real source — not build output.** A name search matches compiled
   artifacts too. Filter them out:
   ```bash
   find <old-repo> -iname "*<name>*" -not -path "*/out/*" -not -path "*/build/*" \
        -not -path "*/target/*" -not -path "*/bin/*" -not -name "*.class"
   ```
   Inner classes show up as `Piece$Type.class` and are noise.

3. **Diff each file against its counterpart in the starter.** If the same path is
   missing, find it by file name; keep the starter's `package`/path and report the move.
   `git diff --no-index --stat <old-repo>/src <starter>/src` lists what differs (exit 1
   means "differences found"). A two-way diff mixes your edits with the professor's, so
   separate them: in the old repo, `git diff $(git rev-list --max-parents=0 HEAD) HEAD -- <file>`
   is what is yours. To combine, `git merge-file -p <starter-file> <old-base-file> <old-file>`
   keeps starter additions and marks real conflicts. Read both before copying.

4. **Verify the dependency surface.** Every symbol the incoming file references must
   exist in the starter — constants, static helpers, and the methods it calls on
   sibling classes. Starters evolve between checkpoints, so this is where a blind copy
   turns into a file that won't compile:
   ```bash
   grep -rnwE "methodA|methodB|CONST_ONE" <starter>/src
   ```
   Check the reverse direction too: every member that starter classes call on the
   incoming class must still exist in the incoming file
   (`grep -rnE "\.(memberA|memberB)\(" <starter>/src`).
   If something is missing or renamed, stop and tell the user before overwriting.

5. **Copy exactly the scope asked.** Other files will also differ. Leave them alone —
   the starter's versions may carry updates the old repo predates.

6. **Confirm the change set.** Run `git status --short` in the starter before and after
   the copy; the difference must be exactly the intended files.

7. **Report.** Say what was copied, what was deliberately left, what you verified, and
   what you did not verify.

## Rules

- **If the starter's version has diverged** — it gained something the old file lacks —
  do not blind-overwrite. Show both sides; merge only when the merge is mechanical
  (no new logic), otherwise give it to the user. Copying his own finished file is not
  authoring, so professor mode does not block it; writing new logic during a merge is.
- **Scope is literal.** "Just copy Piece" means one file, even when four differ.
  Widening the copy quietly reverts the professor's other updates.
- **Don't claim it compiles unless you compiled it.** GUI coursework needs a configured
  toolchain (JavaFX wants `--module-path`), so verification usually belongs in the IDE.
  Say plainly that you didn't build it.
- The old repo's work is the user's own, carried across their own checkpoints. That is
  what these lab sequences are designed for — no need to hedge about it.

## Gotchas

- **Never assume the starter file is a stub.** It usually holds a working stock version.
  Overwriting without reading the diff can silently drop the professor's newer scaffolding.
- **Course header comments travel with the file** and go stale — `Assignment:`, `Date:`,
  `Term:` will still name the old lab. Flag them; let the user set the new values.

## Untested

- Only exercised on a single-file Java/JavaFX port. Multi-file ports, and languages
  where the dependency check needs imports or a build manifest updated too (Python
  packages, C++ headers plus `CMakeLists.txt`), follow the same shape but have not
  been run through it.
- No automated build verification step — every run so far has handed compilation back
  to the user's IDE.
