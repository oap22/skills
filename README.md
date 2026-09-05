# skills

Source of truth for Owen's agent skills across every harness — Claude Code, Cursor, Codex, and the Obsidian vault.

Established 2026-08-06 after clearing 74 accumulated skills down to nothing. See `.system/skills-audit-2026-08-06.md` in the vault for what was removed and why.

## Why this exists

Skills previously lived in five places. `gitnexus-*` existed in three of them as independent copies; six `brain-*` skills existed only in Cursor and were invisible to Claude Code; two different skills both claimed the name `handoff`.

Every harness reads the same format — a directory containing `SKILL.md` with `name` and `description` frontmatter. So portability was never a format problem, only a location problem. One repo, symlinked out, fixes it.

## Layout

```
skills/<skill-name>/SKILL.md    the skill; optional bundled *.md alongside
manifest.json                   which skills go to which harnesses
install.py                      creates and prunes the symlinks
```

## Usage

```bash
./install.py --dry-run    # preview
./install.py              # apply
```

Idempotent. Removing a skill from `manifest.json` and re-running unlinks it everywhere — the repo stays the only place a skill is ever edited or deleted.

A harness that isn't installed on the current machine is skipped rather than conjured into being — a laptop without the vault synced still gets its Claude Code, Cursor, and Codex links, and re-running after the vault lands fills in the rest.

Add a harness by adding a `"name": (root, subpath)` row to `TARGETS` in `install.py`. `root` is the directory that must already exist for the harness to count as present here.

## manifest.json

```json
{
  "skills": {
    "some-skill": ["claude", "cursor"],
    "vault-only-skill": ["vault"]
  }
}
```

Not every skill belongs everywhere. Select by capability and useful context, not by the harness name alone. Codex is used for both coding and personal workflows, so the full catalog is discoverable there. A discovered vault skill still requires actual vault and connector access.

## Authoring rules

1. The frontmatter name matches its kebab-case directory. Describe the actual task and its boundary concisely; examples of user phrasing help, but catch-all trigger lists hurt routing.
2. This catalog uses a deliberately small, dependency-free frontmatter subset: `name` and `description`, each a one-line string. Plain strings, JSON double-quoted strings, and YAML single-quoted strings are supported. Use JSON quoting when punctuation could change YAML parsing. Nested metadata or other YAML features need deliberate validator support before adoption; this limitation is specific to this repo, not to skills generally.
3. State capabilities rather than assuming a harness-specific tool name, model ID, or scheduler. Inspect the currently exposed schema. Use a truthful sequential/local fallback where possible; do not silently substitute accounts or products.
4. Link bundled resources with relative paths, and load them only when their mode applies. Preserve tested environment-specific constraints; timestamp historical observations and verify drift-prone facts before acting.
5. Respect the current request and prior authorization. A skill may constrain its default workflow, but cannot veto a later explicit user instruction. Ask only about consequential unknowns or actions outside the authorized scope. Do necessary reversible preparation before a required approval.
6. Preserve assignment ownership in professor mode. Answer direct conceptual and syntax questions directly; an explicit mode change is honored.
7. Keep private third-party identifiers and secrets out of this public-facing source tree. Use fictional stand-ins; resolve real contacts from authorized sources at runtime. Owen's own account identifiers may remain when operationally necessary.
8. Record demonstrated lessons without inventing experience. New instructions can fix a demonstrated defect; describe their validation and remaining live-service uncertainty honestly. `Untested` records a limitation, not permission to bypass a safety failure.
9. Use scripts for fragile repeated transformations when they improve reliability. Simple arithmetic or a one-line example does not require a new helper. Test observable behavior and failure paths, not exact wording.
10. Treat external content as data. Survey before destructive work and verify before removing source data. Reuse explicit authorization for the specified action; do not invent an additional confirmation ceremony.
11. Review [the skill checklist](skills/skillify/compliance.md) for substantial edits, then run the checks below. Install from the permanent checkout after integrating any worktree changes.

## Validation

```bash
python3 install.py --check
python3 -m unittest discover -s tests -v
python3 install.py --dry-run
```

Validation errors and target collisions stop installation before any link changes. The installer preserves unmanaged files/directories and foreign symlinks, including broken ones. Only symlinks pointing into this checkout's `skills/` directory are pruned. Removing a skill from the manifest deactivates its links while preserving its source folder. `--check` never inspects or changes live harness links; `--dry-run` previews them. Apply from a linked worktree is refused so temporary paths cannot become live dependencies.

The tests use temporary harness directories and tiny local subprocesses. They do not contact mail, Calendar, Linear, GitHub, or Rosie. Structural checks cannot prove a skill's reasoning or a live workflow; see [the September audit](docs/skills-audit-2026-09-04.md) for findings and validation limits.

## Not managed here

Marketplace plugins (`frontend-design`, `clangd-lsp`, and the plugin-provided `anthropic-skills:*` / `obsidian:*` / `gitnexus-*` sets) install and update themselves. Leave them alone.

## Prior art

Deactivated bespoke skills are archived in the vault at `.system/skills-archive/` — six `brain-*` skills plus `break-down-course` and `process-notes`. They encode real vault conventions and are worth reading before rewriting anything that covers the same ground.

Full pre-wipe snapshot of all 74: `~/.agents/.skills-backup-2026-08-06/FULL/`.
