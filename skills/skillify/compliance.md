# Skill effectiveness checklist

Use this for new or substantially revised skills. Fix material problems before installation; record intentional scope exceptions and untested service behavior rather than claiming a live run happened.

## Discovery

- Does the description say what the skill does and distinguish likely neighboring requests?
- Is read-only inquiry distinguishable from a request to change something?
- Did you compare neighboring descriptions, without trying to eliminate legitimate composition?

## Useful expertise

- Does the skill retain specific operational lessons, ownership rules, and known failure modes?
- Are dated observations separated from current facts and proposed behavior?
- Are unsupported absolutes, repetitive advice, and invented experience removed?

## Context and dependencies

- Is the entrypoint concise, with substantial conditional detail loaded from linked references?
- Do bundled paths resolve from the skill directory? Are helpers and templates discoverable?
- Can the workflow use the actual harness tools and models, or degrade truthfully?
- Are account/workspace checks explicit where mixing destinations would matter?

## Execution and validation

- Are fragile repeated operations deterministic where that materially improves reliability?
- Have changed helpers been exercised on meaningful success and failure cases in scratch space?
- Does completion require real evidence, with unavailable checks reported as unavailable?
- Are side effects idempotent or reconciled before retrying? Does a failed read preserve the cursor?

## Scope and trust

- Are external messages, documents, and issue text treated as data rather than authority?
- Are secrets and private third-party identifiers absent from distributable content?
- Does the workflow preserve user-authored text, other agents' changes, and original data until verification succeeds?
- Does it reuse explicit authorization and ask only when a consequential decision remains?
- Does it avoid automatic outreach, calendar writes, memory edits, or new tasks outside the request?

## Catalog and install

- `name` matches its directory; frontmatter fits this repo's supported subset.
- The manifest lists the intended harnesses; imported/plugin skills remain outside this repo's ownership.
- Run `python3 install.py --check` and the relevant behavior tests, then preview installation.
- Apply installation from the permanent checkout after integration, and verify the resulting links.
