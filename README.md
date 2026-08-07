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

Add a harness by adding a row to `TARGETS` in `install.py`.

## manifest.json

```json
{
  "skills": {
    "some-skill": ["claude", "cursor"],
    "vault-only-skill": ["vault"]
  }
}
```

Not every skill belongs everywhere. Vault skills are meaningless in a coding harness; refactoring skills are meaningless in the vault.

## Authoring rules

1. `name` matches the directory name, kebab-case.
2. `description` is one line, third person, and **names its trigger phrases**. Every harness routes on this string — a vague description is a skill that never fires.
3. **Don't hardcode harness-specific tool names in load-bearing steps.** A skill that says "spawn subagents with the Task tool" breaks *silently* in Cursor. Describe the capability and degrade: "if parallel subagents are available, fan out; otherwise process sequentially." This is the real portability constraint.
4. Reference bundled files by relative path, never absolute.
5. Keep `SKILL.md` short; push detail into bundled `.md` files loaded on demand.
6. Absolute vault paths are acceptable in `vault`-targeted skills only.
7. **Never name a real third party.** This repo is pushed off the machine; the people in Owen's mail and calendar didn't agree to that. Examples use fictional stand-ins (`Dr. Vance`, `jordanm@example-corp.com`), and the real name or address gets resolved from Gmail or the vault at runtime. Owen's own addresses are fine — they're load-bearing in `draft-outreach` and `log-outreach`.

## Not managed here

Marketplace plugins (`frontend-design`, `clangd-lsp`, and the plugin-provided `anthropic-skills:*` / `obsidian:*` / `gitnexus-*` sets) install and update themselves. Leave them alone.

## Prior art

Deactivated bespoke skills are archived in the vault at `.system/skills-archive/` — six `brain-*` skills plus `break-down-course` and `process-notes`. They encode real vault conventions and are worth reading before rewriting anything that covers the same ground.

Full pre-wipe snapshot of all 74: `~/.agents/.skills-backup-2026-08-06/FULL/`.
