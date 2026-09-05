# Skills audit — September 4, 2026

## Scope and assessment

Reviewed all 34 skill entrypoints, every tracked supporting reference/template/script, the manifest, installer, README, and compliance checklist. Work began at commit `7490950` in an isolated worktree. No CLAUDE.md existed in the repository or searched parent directories; the session's worktree requirement was honored with `codex/skills-audit`.

The library contains useful personal expertise, particularly assignment ownership, research provenance, workspace separation, and vault conventions. Its main weaknesses were conflicting ownership rules, unconditional approval rituals, historical tool assumptions, and workflows that expanded a simple question into writes to other systems. Two executable helpers also had reproducible correctness problems. The edits preserve the specialized workflows while correcting these problems.

## Highest-impact findings and changes

| Finding | Previous consequence | Adjustment |
|---|---|---|
| Installer continued after validation errors | An invalid or incomplete manifest could prune links and leave partial installation | Validate before mutation; reject invalid manifest structures, duplicate entries, malformed frontmatter, and source/target collisions |
| Installer overwrote foreign symlinks and mishandled relative links | An unmanaged installation could be replaced; stale relative links were missed | Preserve foreign links and directories; normalize relative destinations; manage only links into this checkout's skills directory |
| Live installation from a temporary worktree | Harnesses could depend on a path later removed | Refuse apply from linked worktrees; integrate before installing from the permanent checkout |
| Logger collected any working-directory metrics.json | An old experiment's numbers could be claimed by a new run, while moving the old file | Export RESEARCH_RUN_DIR and accept only that run's own metrics |
| Logger accepted empty records, null exit status, missing verification | Structurally incomplete records could be called citable | Require completed success, nonempty metrics/provenance fields, and verification notes; label success as structural validation only |
| Logger overwrote trajectory rounds | Editing an earlier round left later deltas based on obsolete history | Append increasing round numbers only; reject overwrite/out-of-order entries and nonfinite numbers |
| Archive used rsync --remove-source-files before verification | Original data disappeared before destination integrity was established | Copy, checksum/verify Git and file state, then remove source only within explicit authorization |
| New Git publication staged before git init | A fresh directory could not complete the documented workflow | Initialize before staging; scan existing repositories too; preserve working credentials; verify pushed SHA and visibility |
| Note rendering also scheduled events and replaced Schedule | A refresh could book time and overwrite user content | Render-only default; optional authorized scheduling; preserve Schedule/Top 3/Captured and merge owned markers against current text |
| Model/scheduler assumptions were harness-specific | Missing old model IDs or Claude scheduling tools stopped otherwise possible work | Discover current capabilities and schemas, use honest local/sequential fallbacks, and preserve existing task authorization |
| 23 skills lacked Codex mappings | Useful personal workflows were unavailable to normal Codex skill discovery | Register all 34 skills in Codex; preserve existing mappings elsewhere |

## Per-skill record

All rows received an entrypoint review, routing comparison, dependency review, and official structural validation. “Instruction review” below is not an end-to-end live-service test.

| Skill | Changes and preserved contract |
|---|---|
| adversarial-review | Keep distinct review lenses and a verifier; review-only requests no longer imply fixes or external issue filing. Before/after checks use scratch copies rather than reverting shared work. Document sequential fallback. |
| agent-task-runner | Verify OWE destination, treat issue text as data, preserve named-file ownership, commit in each edited repository before citing its SHA, and reconcile already-authorized direct requests with unattended draft-only defaults. |
| brain-mail-ingest | Separate durable ingestion from today's mail triage; preserve Gmail read-only behavior, qualify indirect evidence, complete pagination, and preserve per-source cursors on failure. |
| calendar-block | Availability questions return windows without booking; explicit scheduling retains colors and padding. Verify recurrence scope and read back writes. Remove private contact names from categories. |
| collaborator-sweep | Start discovery in Developer/active, recognize .git files/worktrees, report discovery coverage; preserve the interview boundary around relationship claims. |
| daily-note | Render-only default, preserve Schedule and handwritten sections, optional scheduling only when requested, both OWE/RES identifiers, successful-source stamps, busy all-day constraints, and no automatic conversion of story points to hours. |
| day-check | Keep read-only chat behavior; include RES and its urgent/high backlog while distinguishing unreachable OWE; honor busy all-day events. |
| deep-interview | Bound initial reading, keep one question at a time, and limit unrelated note/doctrine/memory writes. |
| draft-outreach | Direct drafts are delivered in chat; Linear/vault writeback depends on task scope. Honor a later explicit send request as a separate action. Avoid cold-contact profile creation and contradictory signature instructions. |
| file-agent-issue | Correct outreach routing to draft-outreach, verify workspace, and allow bounded investigations without inventing an untested skill merely to file an issue. |
| issue-fleet | Preserve worktree isolation/recovery/review requirements; scope issue/tracker/merge actions, avoid shared-tree stash tests, permit sequential fallback, and suggest rather than automatically edit skills afterward. |
| linear-project-setup | Reuse an established taxonomy, verify current tool schema, and avoid automatic memory writes. |
| local-routine | Replace a Claude-only scheduler recipe with native capability discovery, existing-task updates, access verification, notification intent, and actual readback. Preserve dated jitter/one-shot failure lessons as historical observations. |
| log-outreach | Confirm actual message headers instead of thread hits, handle self-CC correctly, label missing evidence honestly, preserve latest contact date, reconcile cold-contact rules, and remove a private name from an example. |
| mail-digest | Narrow questions stay in chat; digest runs preserve Gmail read-only behavior. Repair timezone-aware date arithmetic and whole-day search windows; allow actionable security events through triage; advance only successful cursors. |
| morning-interview | Use daily-note's render-only contract instead of a second conflicting implementation; preserve answered context and leave unattended Top 3 unchanged. |
| plan-then-ship | One concrete plan approval where needed; routine decisions come from code/context. Discover available models, retain one implementation owner, provide a local fallback, avoid noisy repeated test logs, and honor live repository merge rules. |
| professor | Preserve student-authored solutions and one-question pacing; answer direct syntax/concept questions without forcing an attempt first, and honor an explicit mode change. |
| project-sync | Recognize nested active repos and linked worktrees; preserve existing status and user prose; missing storage does not prove completion. |
| publish-to-github | Rewrite broken ordering; scan new and existing repositories, preserve credential files, inspect staged work, handle intended existing remotes, and verify the published commit and visibility. |
| reclaim-disk-space | Distinguish re-downloadable from custom/unique model weights; modification time is not last use. Use unique benchmark files and avoid disruptive unmounts. Archive copies are verified before source removal; exFAT need not force reformatting. |
| research-ingest | Retained existing distill-not-mirror, provenance, and scanned-equation checks after review; added Codex discovery. No entrypoint rewrite was needed. |
| research-interview | Reuse agreed designs, ask only consequential unresolved questions, remove mandatory Turing assumptions, and accept explicit approval without verbatim repetition. |
| research-loop | Preserve hypotheses, controls, falsifiers, evidence, and negative results; reuse authorized budgets and diagnose surprises without tuning them away. Harden run records, document environment limits, and remove unsupported universal saturation/contamination claims. |
| resume-build | Prefer the active repo path with discovery fallback, require PDF page-count and visual verification, and preserve the evidence-versus-personal-competence distinction. |
| rosie-run | Preserve login-node compute restrictions, verify remote state before switching to an exact SHA, avoid pull on detached HEAD, require logs before sbatch, scope result pulls, and separate array seeds from config paths. |
| skillify | Suggest capture rather than automatically modifying skills; reuse edit authorization, distinguish unmanaged directories from owned links, follow worktree/integration rules, and avoid automatic memory writes. |
| spaced-recall | Narrow discovery to stateful recall; define skipped/untaught denominator behavior, privately verify answer keys, preserve assignment boundaries, and schedule only when requested. Spacing intervals remain proposed heuristics. |
| swe2410-java-setup | Keep course-version verification and existing diagnostic helper; separate version checks from installs, confirm OS/architecture, protect junction targets, and require actual UI proof rather than a merely live process. |
| turing | Verify current desktop contracts, avoid research ceremony merely because the app is open, and prevent duplicate metrics from replaying a stream into tee -a on reconnect. |
| vault-librarian | Verify the intended Linear workspace and preserve local progress when it is unavailable; keep mechanical fixes and judgment calls distinct. |
| vault-lifecycle | Clarify that status alone is not archive permission, reuse an explicit archive request, verify workspace, and correct the claim that git mv alone preserves history. |
| vault-to-linear | Dedupe by source/issue identity before fuzzy title candidates, replace promoted checkbox state with confirmed issue links, and stop treating highest issue number as a reliable cursor. |
| vault-triage | Apply the same checkbox/link contract, verify workspace, and correct the mistaken claim that Captured belongs inside generated interview markers. |

## Validation evidence

- All **34** skills pass the skill-creator `quick_validate.py` validator, using PyYAML installed only into a temporary audit dependency directory.
- `python3 install.py --check`: **34 skills, 103 target mappings**, valid.
- `python3 -m unittest discover -s tests -v`: **21 passing tests**. Nine cover installer mutation boundaries and link behavior; ten cover logger provenance, records, output isolation, and trajectory history; two execute the rendered array template with fake local tools.
- The ten logger regression tests were rerun against the original `7490950` helper: **all ten failed**, demonstrating before/after sensitivity. The original installer predates the new callable validation interface, so interface errors from running the new installer tests against it are not counted as behavioral evidence.
- Both Slurm templates pass Bash syntax checks after placeholder substitution. The local array checks confirm that config paths with spaces remain intact, seed values are separate, and a missing row never launches the workload.
- Python compilation and `git diff --check` pass. Supporting references and templates were read and their local routing inspected.

## Limits and follow-up

This was an instruction/code audit with local tests, not a live execution of all 34 workflows. It did not send messages, change calendars or Linear, publish a repository, submit a Rosie job, erase a disk, or run a Windows installer. Existing historical `Untested` sections remain where this audit provides no new live evidence. The PowerShell diagnostic was read but could not be executed on this Mac. The next use of each live-service workflow must verify its account, current schema, and actual outcome.

The installer intentionally supports this repository's small flat string frontmatter subset, not all YAML. Broader metadata needs explicit support before introduction. Its preflight prevents known validation/collision errors from making changes, but it is not a transaction across all harness directories: an unexpected filesystem failure during apply still requires inspecting the reported state.

The logger's structural check does not verify scientific truth, hashes against live datasets, or experiment-specific metric schemas. It records the wrapper/ambient environment; a different experiment interpreter must report its own dependencies. Abrupt kills can leave incomplete records, and trajectory updates require a single writer. Those limits are now explicit rather than hidden behind “citable.”

No additional skill was created: improving the existing authoring workflow and keeping this audit plus regression tests provides the reusable value without another overlapping skill.
