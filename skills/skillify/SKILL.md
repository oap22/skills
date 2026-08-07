---
name: skillify
description: Turn a finished session into a reusable skill. Distills what was just done into a portable SKILL.md, registers it in the skills repo, and links it into every harness. Use when the user says "skillify", "make this a skill", "turn this into a skill", "save this workflow", "I don't want to redo this", or when a session ends with a procedure worth repeating.
---

# Skillify

Distill a session into a skill so the same work never gets rebuilt from scratch.

**Repo:** `~/Developer/skills` — the source of truth for every harness.
**Never** write a skill directly into `~/.claude/skills`, `~/.cursor/skills`, `~/.codex/skills`, or a vault `.claude/skills`. Those are symlink targets and hand-placed directories get pruned.

## The Bar

Most sessions are not skills. Apply this before writing anything.

**A skill is a procedure you would run again on different inputs.** If the same steps would produce useful results next month with a different file, repo, or topic, it qualifies.

Route everything else to its real home instead of manufacturing a bad skill:

| What the session actually produced | Where it belongs |
|---|---|
| Repeatable procedure, variable inputs | **A skill** — continue |
| A fact about this project or codebase | `CLAUDE.md` / `AGENTS.md` |
| A durable preference about how to work | Memory, if the harness has one |
| A one-off fix, or exploration of one specific bug | Nowhere — say so and stop |
| Something an existing skill already covers | **Improve that skill instead** |

Say plainly when a session doesn't clear the bar. A skill that never fires is worse than no skill: it dilutes description-matching for everything else.

## Steps

### 1. Get the session content

In order of preference:

1. **The current conversation** — the default, and available in every harness.
2. **A past session**, if the user names one *and* this harness exposes session-transcript tools. Search for it, read it, confirm you found the right one before proceeding. If those tools aren't available here, say so and ask the user to point at a file or paste the relevant part.
3. **A file or paste** the user provides.

### 2. Check for overlap first

Read `~/Developer/skills/manifest.json` and the `description` line of each existing skill in `~/Developer/skills/skills/*/SKILL.md`.

If an existing skill covers this ground, **improve it rather than adding a second one**. Two skills with overlapping descriptions compete for the same requests and both fire unreliably — this is the single most common way a skill library rots.

If the session shows the user *redoing* work an existing skill should have handled, that skill's `description` is the likely culprit. Fix the description.

### 3. Extract the procedure

Work out what was actually done, then separate the reusable shape from this session's specifics:

- **Inputs** — what varied, and what would vary next time. These become the skill's parameters.
- **Steps** — the ordered actions, with the judgment calls that made them work.
- **Rules** — constraints discovered the hard way. These are the most valuable part; they're what a fresh agent won't know.
- **Failure modes** — anything that went wrong and how it was resolved. Include these; they're why the skill beats improvising.

Strip session specifics. A concrete path from this session becomes an input, not a constant — unless the skill is genuinely bound to one location, which is legitimate for vault skills.

### 4. Write the description

This is the whole routing mechanism. Every harness matches requests against it. Get it wrong and the skill never fires.

- One line, third person, starts with what it does.
- Name the **trigger phrases** the user would actually say — their words, not formal ones.
- Be specific enough to *not* match neighboring requests. `description: helps with code` matches everything and therefore nothing.

Pattern: `<What it does>. Use when the user says "<phrase>", "<phrase>", or <situation>.`

### 5. Draft SKILL.md

```markdown
---
name: <kebab-case, matches directory name>
description: <see step 4>
---

# <Title>

<One or two lines: what this does and when it applies.>

## Steps

1. <Imperative. Numbered. Concrete.>

## Rules

- <Constraints, gotchas, things learned the hard way.>
```

Keep it short. Push long reference material into sibling `.md` files in the same directory and point at them by relative path — they get read on demand rather than every time the skill loads.

### 6. Check portability

The real constraint is not frontmatter — it's tool assumptions.

**A skill that hardcodes a harness-specific tool in a load-bearing step breaks silently in other harnesses.** Describe the capability and degrade:

> If parallel subagents are available, fan out one per topic; otherwise process them sequentially.

Not:

> Use the Task tool to spawn one subagent per topic.

Also: relative paths for bundled files, never absolute. Absolute vault paths are fine in `vault`-targeted skills only.

### 7. Install

1. Write to `~/Developer/skills/skills/<name>/SKILL.md`.
2. Add to `manifest.json` under `skills`, mapping the name to its harnesses:
   - `claude`, `cursor`, `codex` — general coding and workflow skills
   - `vault` — **only** for skills specific to the Obsidian vault. Global Claude Code skills already resolve inside the vault, so adding both `claude` and `vault` registers it twice.
3. Run `cd ~/Developer/skills && ./install.py` and confirm the links.
4. Commit: `skillify: add <name>`.

### 8. Report

- Skill name and path
- Its description, quoted — so the user can judge whether it will fire
- Harnesses linked
- Anything from the session deliberately left out, and why

## Rules

- **Apply the bar honestly.** Declining to make a skill is a valid, useful outcome. Say what the session produced instead.
- **One skill per procedure.** If the session contained two unrelated procedures, make two skills or ask which to build.
- **Never hand-place a skill** in a harness directory — it gets pruned by `install.py`.
- **Prefer improving an existing skill** over adding an overlapping one.
- **Include the failure modes.** The mistakes are the value; a procedure without them is just a summary.
- **Don't invent steps that weren't taken.** The skill records what actually worked, not an idealized version. If a gap needs filling, mark it explicitly as untested.
- **Ask before overwriting** an existing skill's `SKILL.md`.
