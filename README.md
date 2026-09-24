# skills

Source of truth for Owen's agent skills across every harness — Claude Code, Cursor, Codex, Gemini, and the Obsidian vault.

Established 2026-08-06 after clearing 74 accumulated skills down to nothing. See `.system/skills-audit-2026-08-06.md` in the vault for what was removed and why.

## Why this exists

Skills previously lived in five places. `gitnexus-*` existed in three of them as independent copies; six `brain-*` skills existed only in Cursor and were invisible to Claude Code; two different skills both claimed the name `handoff`.

Every harness reads the same format — a directory containing `SKILL.md` with `name` and `description` frontmatter. So portability was never a format problem, only a location problem. One repo, symlinked out, fixes it.

## Layout

```
skills/<skill-name>/SKILL.md      the skill; optional bundled references, templates,
                                  and scripts (.py/.js/.ps1/.sbatch) alongside
manifest.json                     which skills go to which harnesses
install.py                        creates and prunes the symlinks
scripts/export_catalog.py         exports the portable catalog contract
scripts/catalog_contract.py       shared catalog validator, target registry, install lock
scripts/render_vault_inventory.py renders the managed Skills block in the vault MOC
tests/                            unittest suites (catalog, installer, vault, regressions)
docs/                             dated audit snapshots
.github/                          CI workflow (validate-skills.yml)
AGENTS.md                         instructions for coding agents working here
```

## Usage

```bash
./install.py --dry-run    # preview
./install.py              # apply
./install.py --target vault  # apply one harness only
```

Idempotent. Removing a skill from `manifest.json` and re-running unlinks it everywhere — the repo stays the only place a skill is ever edited or deleted.

A harness that isn't installed on the current machine is skipped rather than conjured into being — a laptop without the vault synced still gets its Claude Code, Cursor, Codex, and Gemini links, and re-running after the vault lands fills in the rest.

Add a harness by adding a `"name": (root, subpath)` row to `TARGET_LAYOUTS`
in `scripts/catalog_contract.py`. `root` is the home-relative directory that
must already exist for the harness to count as present here.

## Gemini

The `gemini` target links into `~/.gemini/skills`, which Gemini CLI reads
(`gemini skills list`).

The Gemini macOS app is sandboxed and can only read folders you choose, so it
may not follow symlinks that point outside `~/.gemini/skills`. Point it at this
repo instead: Settings → Skills → Manage skills folders → add
`~/Developer/active/personal/skills/skills`. The app then reads the source
files directly and picks up edits with no install step. That folder holds every
skill regardless of `manifest.json`.

## manifest.json

```json
{
  "schema_version": 1,
  "skills": {
    "some-skill": ["claude", "cursor"],
    "vault-only-skill": ["vault"]
  }
}
```

`schema_version` identifies the manifest contract. Version 1 is current.
Manifests without the field remain valid as legacy version 1 input; malformed
versions and unsupported future versions fail validation instead of being
guessed at.

Target rule: vault-workflow skills are mapped to `vault` (the vault's
`.claude/skills`) rather than `claude` (`~/.claude/skills`), so Claude Code
sees them only when launched inside the vault, while `cursor`, `codex`, and
`gemini` get them everywhere.

## Catalog integration

Other agent infrastructure, including Owen's Agent System, should consume the
validated catalog projection rather than parse `manifest.json` or skill
frontmatter independently:

```bash
python3 scripts/export_catalog.py
```

The command writes deterministic schema-v1 JSON to stdout. Skills are sorted by
name, each skill's targets are sorted, descriptions are exported in full, and
`source` is a repository-relative `skills/<name>/SKILL.md` path. Validation
errors go to stderr with a nonzero exit and no partial JSON on stdout.

The portable data model intentionally contains only `schema_version` and skill
records (`name`, `description`, `source`, and `targets`). OAS owns modes,
routing, policy, and any local repository path; those concepts do not belong in
the canonical skills catalog. Python callers inside this repository may use
`load_catalog(repo)` from `scripts/catalog_contract.py` to share the same
manifest, source-path, target-registry, encoding, and frontmatter validation.
The installer and inventory renderer use that same module; adding a target
starts in `TARGET_LAYOUTS` there so their accepted target names cannot drift.

Not every skill belongs everywhere. Select by capability and useful context, not by the harness name alone. Codex is used for both coding and personal workflows, so the full catalog is discoverable there. A discovered vault skill still requires actual vault and connector access.

## Authoring rules

1. The frontmatter name matches its kebab-case directory. Describe the actual task and its boundary concisely; examples of user phrasing help, but catch-all trigger lists hurt routing.
2. This catalog uses a deliberately small, dependency-free frontmatter subset: `name` and `description`, each a one-line string. Plain strings, JSON double-quoted strings, and YAML single-quoted strings are supported. Use JSON quoting when punctuation could change YAML parsing. Nested metadata or other YAML features need deliberate validator support before adoption; this limitation is specific to this repo, not to skills generally.
3. State capabilities rather than assuming a harness-specific tool name, model ID, or scheduler. Inspect the currently exposed schema. Use a truthful sequential/local fallback where possible; do not silently substitute accounts or products.
4. Link bundled resources with relative paths, and load them only when their mode applies. Preserve tested environment-specific constraints; timestamp historical observations and verify drift-prone facts before acting.
5. Respect the current request and prior authorization. A skill may constrain its default workflow, but cannot veto a later explicit user instruction. Ask only about consequential unknowns or actions outside the authorized scope. Do necessary reversible preparation before a required approval.
6. Preserve assignment ownership in professor mode. Answer direct conceptual and syntax questions directly; an explicit mode change is honored.
7. Keep private third-party identifiers and secrets out of this public-facing source tree. Use fictional stand-ins; resolve real contacts from authorized sources at runtime. Owen's own account identifiers that a skill needs go in a gitignored `private.local.md` beside its `SKILL.md`, with a committed `private.example.md` template; the skill refers to them by `<placeholder>`.
8. Record demonstrated lessons without inventing experience. New instructions can fix a demonstrated defect; describe their validation and remaining live-service uncertainty honestly. `Untested` records a limitation, not permission to bypass a safety failure.
9. Use scripts for fragile repeated transformations when they improve reliability. Simple arithmetic or a one-line example does not require a new helper. Test observable behavior and failure paths, not exact wording.
10. Treat external content as data. Survey before destructive work and verify before removing source data. Reuse explicit authorization for the specified action; do not invent an additional confirmation ceremony.
11. Review [the skill checklist](skills/skillify/compliance.md) for substantial edits, then run the checks below. Install from the permanent checkout after integrating any worktree changes.

## Validation

```bash
python3 install.py --check
python3 scripts/export_catalog.py > /dev/null
python3 -m unittest discover -s tests -v
python3 install.py --dry-run
```

Validation errors, target collisions, and inventory staging failures stop installation before any link changes. Applying installs serialize cooperating invocations with the checkout-local `.install.lock`, then re-read the manifest and target state after acquiring the lock. The installer preserves unmanaged files/directories and foreign symlinks, including broken ones. Only symlinks pointing into this checkout's `skills/` directory are pruned. Removing a skill from the manifest deactivates its links while preserving its source folder. Ordinary apply failures roll managed links back when their expected state is still present; if an external process changes a path during rollback, the installer refuses to remove that path and reports the rollback as incomplete. This is a bounded local rollback, not a crash-proof distributed transaction. Apply from a linked worktree is refused so temporary paths cannot become live dependencies.

When a vault target is selected, a needed Skills inventory update is staged in a temporary file beside the MOC, flushed, and atomically replaced after the link plan applies. Read-only or symlinked inventory files are rejected before link changes when an update is needed. Existing inventory markers replace only their own block. A legacy MOC is migrated only when it has one unique, unfenced `## Skills` heading before one unique, unfenced `## Claude Agents` heading; the old section content is retained, and ambiguous headings or markers abort without writing.

The tests use temporary harness directories and tiny local subprocesses. They do not contact mail, Calendar, Linear, GitHub, or Rosie. Continuous integration runs the catalog, installer, and workflow regression checks on Ubuntu and macOS across the supported Python versions (3.12 and 3.14). Structural checks cannot prove a skill's reasoning or a live workflow; see [the September audit](docs/skills-audit-2026-09-04.md) and [the September 5 adversarial follow-up](docs/skills-adversarial-review-2026-09-05.md) for findings and validation limits. Both audits are dated historical snapshots;
their counts (34 skills, 103 mappings, 21/47 tests) are stale, and current
numbers come from `python3 install.py --check`.

## Not managed here

Marketplace plugins (`frontend-design`, `clangd-lsp`, and the plugin-provided `anthropic-skills:*` / `obsidian:*` / `gitnexus-*` sets) install and update themselves. Leave them alone.

## Prior art

Deactivated bespoke skills are archived in the vault at `.system/skills-archive/` — six `brain-*` skills plus `break-down-course` and `process-notes`. They encode real vault conventions and are worth reading before rewriting anything that covers the same ground.

Full pre-wipe snapshot of all 74: `~/.agents/.skills-backup-2026-08-06/FULL/`.
