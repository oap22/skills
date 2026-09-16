# Skills adversarial review — September 5, 2026

## Scope

Follow-up to [the full September 4 catalog audit](skills-audit-2026-09-04.md). The review includes that audit, the pending vault workflow/inventory changes preserved from the permanent checkout, and the fixes described here. Work is isolated on `codex/skills-adversarial-finish`; the original pending files were hashed before copying and checked for drift before integration.

Three Luna agents at xhigh reviewed and fixed separate areas: installer/inventory integrity, research records, and skill instruction boundaries. Fresh Luna xhigh agents independently verify the resulting changes before merge. Review evidence distinguishes code reproductions from instruction scenarios and live-service execution.

## Findings addressed

| Area | Concrete failure | Change |
|---|---|---|
| Inventory migration | A fenced example heading could be mistaken for the live Skills section and replace user text | Recognize unique unfenced legacy headings, preserve legacy text, and reject ambiguous markers |
| Installation | An unwritable inventory or failed link creation could leave a partially applied installation | Stage inventory writes before link mutation, serialize cooperating installers and replan, restore links on ordinary apply failure, report incomplete rollback |
| Standalone inventory renderer | A string-valued harness list was interpreted character by character | Validate manifest and skill inputs before writing |
| Research records | Missing Git provenance and malformed seed/count/hash values passed structural validation | Require complete typed run records, explicit applicability, hash formats, and regular citation files |
| Metric updates | Concurrent successful writers silently lost each other's fields | Lock the entire read/modify/write operation and atomically replace the file |
| Trajectories | A missing run or a first round numbered 3 could be accepted as a baseline | Require a completed backing run, round 0 then consecutive appends, explicit costs/secondary score/interventions, matching eval identity and noise floor |
| Mail workflow | A scheduled digest could create commitments and another unfiled ledger despite owning only the mail block and cursor | Keep durable ingestion behind the authorized single-owner handoff; morning interview reads the existing mail block |
| Lifecycle and doctrine | A status question could trigger metadata/Linear edits, and routine sync could rewrite doctrine | Keep status questions read-only and policy revisions separately scoped |
| Rosie | A dirty local checkout could push and run older committed code while appearing current; scratch cleanup contradicted retention | Require an explicit chosen code state and scoped cleanup authorization |
| Interview and Turing | Broad reading and mandatory fresh interviews repeated work already settled | Bound context reads and materialize already-approved designs |
| Follow-up installer review | Replacement-link failure lost the old target; a fence with trailing text exposed an example block to replacement | Track intermediate replacement state for rollback and require valid whitespace-only closing fences |
| Follow-up research review | Malformed historical counts raised a traceback; removed backing runs stayed in growing trajectories | Validate types before comparisons and revalidate historical backing records, IDs, and eval identity before appending |
| Follow-up instruction review | Day check missed Chosen outcome; stock Windows lacked the required PowerShell executable; approval exceptions were too broad | Honor the chosen outcome with legacy fallback, resolve the installed shell, and keep real trust/secret/destructive-write failures as blockers |
| Validation | Local checks had no automatic cross-platform gate | Add pinned GitHub Actions checks on macOS/Linux and Python 3.12/3.14, with whitespace validation across the full change |

## Rejected or narrowed findings

A proposed daily-note concurrency defect was not sustained: inspection of the actual vault helper confirmed a file lock, expected-bytes comparison, and atomic replacement. The skills now require that verified helper contract and report a blocker if unavailable. This is a documentation clarification, not a claim that the existing helper lacked locking.

A proposed requirement for CI to validate the user's live vault inventory was rejected. That file is outside this repository and is not committed here; checking it on a GitHub runner cannot establish freshness. CI exercises the renderer against isolated fixtures, while permanent-checkout installation and its readback verify the actual inventory separately. A worktree preview reporting permanent-checkout links as foreign is expected and does not justify replacing those links.

The original audit remains a dated record of its 21-test result and then-current limits. This follow-up supersedes its statements that unexpected ordinary installer failures have no rollback and that metric updates rely on a single writer.

## Validation and limits

- Catalog validation: **34 skills / 103 target mappings**.
- Official skill-creator validator: **34/34 passed**, including the final changed descriptions.
- Full-catalog inventory scratch check: **34 rows**, legacy/user text preserved, repeat generation unchanged.
- Independent research verifier: original two findings reproduced, then fixed and replayed successfully; 64 concurrent metric writers retained all fields. Structural checks and the logger regression suite passed.
- Independent instruction verifier: accepted scope/routing/Windows/authoring findings fixed; two residual contradictory sentences were corrected and the focused rereview is clear. This is scenario review, not live workflow execution.
- Installer regression evidence against `b865486` in scratch: replacement failure left the old link absent, and an invalid closing fence exposed example text to replacement. The fixed implementation restores the exact raw relative symlink target and rejects the fenced markers without changing the MOC.
- Parent final local suite: **47 passing tests**. Python compilation and whitespace checks passed.
- Initial PR CI: all four macOS/Linux and Python 3.12/3.14 jobs passed. [PR #4 checks](https://github.com/oap22/agent-skills/pull/4/checks) provide updated-branch CI evidence; merge is gated on all four final checks and the independent verifier conclusions.

This audit does not execute all 34 skills against live mail, calendar, Linear, Rosie, Windows, or other external services. Instruction scenarios cannot establish live workflow success. Structural research validation does not prove scientific truth, the existence of a Git object, or that a declared dataset digest matches real data. Dirty-code provenance still requires scientific review.

Installer rollback covers ordinary process-level failures, not a crash-proof transaction across multiple filesystems or arbitrary writers that ignore its lock. Research lock files left by a killed writer require inspection before removal. Neither an unavailable service nor an interrupted run is reported as successful.
