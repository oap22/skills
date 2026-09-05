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
| Validation | Local checks had no automatic cross-platform gate | Add pinned GitHub Actions checks on macOS/Linux and Python 3.12/3.14 |

## Rejected or narrowed findings

A proposed daily-note concurrency defect was not sustained: inspection of the actual vault helper confirmed a file lock, expected-bytes comparison, and atomic replacement. The skills now require that verified helper contract and report a blocker if unavailable. This is a documentation clarification, not a claim that the existing helper lacked locking.

The original audit remains a dated record of its 21-test result and then-current limits. This follow-up supersedes its statements that unexpected ordinary installer failures have no rollback and that metric updates rely on a single writer.

## Validation and limits

Final check and merge evidence is recorded below after independent verification.

This audit does not execute all 34 skills against live mail, calendar, Linear, Rosie, Windows, or other external services. Instruction scenarios cannot establish live workflow success. Structural research validation does not prove scientific truth, the existence of a Git object, or that a declared dataset digest matches real data. Dirty-code provenance still requires scientific review.

Installer rollback covers ordinary process-level failures, not a crash-proof transaction across multiple filesystems or arbitrary writers that ignore its lock. Research lock files left by a killed writer require inspection before removal. Neither an unavailable service nor an interrupted run is reported as successful.
