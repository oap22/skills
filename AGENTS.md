# skills

Source of truth for Owen's agent skills. Edit skills only here; `install.py` symlinks them into ~/.claude, ~/.cursor, ~/.codex, ~/.gemini and the Obsidian vault.

## Layout
- `skills/<name>/SKILL.md` plus bundled references, templates, and scripts, linked by relative path
- `manifest.json` maps each skill to harnesses; `scripts/catalog_contract.py` owns validation and `TARGET_LAYOUTS`
- `scripts/export_catalog.py` (catalog JSON), `scripts/render_vault_inventory.py` (vault MOC block), `tests/` (unittest)

## Commands
```
python3 install.py --check
python3 scripts/export_catalog.py > /dev/null
python3 -m unittest discover -s tests -v
python3 install.py --dry-run   # preview; apply only from the permanent checkout, never a worktree
```

## Rules
- Frontmatter: only one-line `name` (matches the directory, kebab-case) and `description`.
- New or changed skills follow the README "Authoring rules" and `skills/skillify/compliance.md`.
- No secrets or private third-party identifiers; timestamp cluster and tool facts that drift.
- Do not edit plugin skills (anthropic-skills:*, obsidian:*, gitnexus-*); they are not managed here.
