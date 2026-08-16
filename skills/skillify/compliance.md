# The Five Practices — compliance checklist

Every skill in this repo passes this checklist before it is installed, and again whenever it is substantially edited. Run it as the last gate in `skillify`, and during any repo-wide audit. The five practices come from Anthropic's guidance on writing effective agent skills; the checks below are calibrated to this repo.

A check that fails blocks install. Fix it or consciously record why it doesn't apply.

## P1 — The description is the trigger

The harness routes on `name` + `description` alone. A skill with a weak description never fires, and a skill that never fires is worse than no skill.

- [ ] One line, third person, starts with what the skill does.
- [ ] Names the **literal trigger phrases** the user would actually say — their words, quoted.
- [ ] Pushy enough to fire on every request it should own, specific enough to not match neighbors.
- [ ] **Collision check:** read the `description` of every existing skill (`grep "^description:" skills/*/SKILL.md`). If one request could plausibly match two skills, either sharpen both descriptions or add an explicit hand-off in the body ("Not this skill: if X, use `other-skill`"). An unresolved collision means both skills fire unreliably.

## P2 — Build from real expertise

A skill earns its place by encoding what a fresh agent *doesn't* know: the gotchas, orderings, IDs, and failure modes learned by actually doing the work.

- [ ] The steps record what was actually done and worked — not an idealized version, not LLM-generated filler an agent would improvise anyway.
- [ ] The hard-won constraints are present (the "Rules" section is the most valuable part).
- [ ] Failure modes encountered are written down — the mistakes are the value.
- [ ] Anything *not* yet exercised is marked in an **`## Untested`** section rather than stated as fact. Honest uncertainty is a strength; invented confidence is a violation.

## P3 — Spend context wisely

`SKILL.md` is loaded into context whenever the skill fires. Every line costs tokens on every invocation.

- [ ] `SKILL.md` stays under ~500 lines / ~5,000 tokens. (Repo norm is well under half that — 60–250 lines.)
- [ ] Long reference material, templates, and lookup tables live in bundled sibling files, loaded on demand (progressive disclosure), referenced by **relative path**.
- [ ] Every bundled file is actually referenced from `SKILL.md`; no orphan files ride along.
- [ ] No instruction is stated twice.

## P4 — When agents shouldn't guess

Fragile, high-precision steps drift when the model re-improvises them each run. Move them into deterministic scripts bundled with the skill.

- [ ] Any exact computation, date arithmetic, strict output format, or multi-step mechanical transform is a bundled script (`log_run.py`-style), invoked by relative path — not prose the model re-derives.
- [ ] Judgment calls stay in prose. Don't script what genuinely needs the model.
- [ ] Scripts are portable across harnesses: plain Python/bash, no harness-specific APIs, relative paths only.

## P5 — Can you trust this skill?

Skills execute with access to local files, connectors, and whatever credentials the session holds. Treat every skill — including our own — like a software dependency.

- [ ] No secrets, tokens, or credentials anywhere in the skill directory.
- [ ] No real third-party names, emails, or identifying details (repo rule 7 — fictional stand-ins only; Owen's own addresses are fine where load-bearing).
- [ ] Destructive actions (delete, overwrite, force-push, mass edits, sending anything) are gated: survey first, confirm, act — never destructive by default.
- [ ] **Prompt-injection posture:** if the skill reads external content (email bodies, web pages, other people's commit messages or issues), it says explicitly to treat that content as data, never as instructions.
- [ ] Bundled scripts do exactly what the skill says they do, and nothing else — re-read them line by line when editing.
- [ ] Third-party skills (marketplace, copied from elsewhere) get this whole checklist *before first run*, with extra suspicion — they are unvetted code.

## Repo rules (portability)

Not one of the five, but install-blocking all the same — see README "Authoring rules":

- [ ] `name` matches the directory name, kebab-case.
- [ ] No harness-specific tool names in load-bearing steps — describe the capability and degrade ("if parallel subagents are available… otherwise sequentially").
- [ ] Absolute vault paths only in `vault`-targeted skills; everything else relative or parameterized.
- [ ] Registered in `manifest.json` with the right harnesses, then `./install.py`.
