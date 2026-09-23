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
   project or a personal course repo.

2. **Find the real source — not build output.** A name search matches compiled
   artifacts too. Filter them out:
   ```bash
   find <old-repo> -iname "*<name>*" -not -path "*/out/*" -not -path "*/build/*" \
        -not -path "*/target/*" -not -path "*/bin/*" -not -name "*.class"
   ```
   Inner classes show up as `Piece$Type.class` and are noise.

3. **Diff each file against its counterpart in the starter.** The starter almost always
   already contains a same-named file holding the stock version — often with a
   placeholder like "not yet implemented". The diff is what is actually yours, and it is
   also the survey that justifies the overwrite. Read it before copying.

4. **Verify the dependency surface.** Every symbol the incoming file references must
   exist in the starter — constants, static helpers, and the methods it calls on
   sibling classes. Starters evolve between checkpoints, so this is where a blind copy
   turns into a file that won't compile:
   ```bash
   grep -nE "public .*(methodA|methodB|CONST_ONE)" <starter>/src/**/Sibling.java
   ```
   If something is missing or renamed, stop and tell the user before overwriting.

5. **Copy exactly the scope asked.** Other files will also differ. Leave them alone —
   the starter's versions may carry updates the old repo predates.

6. **Confirm the change set.** `git status --short` in the starter must show exactly the
   intended files and nothing else.

7. **Report.** Say what was copied, what was deliberately left, what you verified, and
   what you did not verify.

## Rules

- **Never assume the starter file is a stub.** It usually holds a working stock version.
  Overwriting without reading the diff can silently drop the professor's newer scaffolding.
- **If the starter's version has diverged** — it gained something the old file lacks —
  do not blind-overwrite. Surface the divergence and merge, or ask.
- **Scope is literal.** "Just copy Piece" means one file, even when four differ.
  Widening the copy quietly reverts the professor's other updates.
- **Course header comments travel with the file** and go stale — `Assignment:`, `Date:`,
  `Term:` will still name the old lab. Flag them; let the user set the new values.
- **Don't claim it compiles unless you compiled it.** GUI coursework needs a configured
  toolchain (JavaFX wants `--module-path`), so verification usually belongs in the IDE.
  Say plainly that you didn't build it.
- The old repo's work is the user's own, carried across their own checkpoints. That is
  what these lab sequences are designed for — no need to hedge about it.

## Untested

- Only exercised on a single-file Java/JavaFX port. Multi-file ports, and languages
  where the dependency check needs imports or a build manifest updated too (Python
  packages, C++ headers plus `CMakeLists.txt`), follow the same shape but have not
  been run through it.
- No automated build verification step — every run so far has handed compilation back
  to the user's IDE.
