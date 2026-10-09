# ADR Format

Adapted from `domain-modeling` in https://github.com/mattpocock/skills (MIT, Copyright (c) 2026 Matt Pocock).

ADRs live in `docs/adr/` (or the context's `docs/adr/` in a multi-context repo) as `NNNN-slug.md`. Scan for the highest number and add one. Create the directory only when the first ADR is needed.

## Template

```md
# {Short title of the decision}

{1-3 sentences: the context, what was decided, and why.}
```

One paragraph is enough. The value is recording that a decision was made and why.

Optional, only when they add value:

- `Status` frontmatter: `proposed | accepted | deprecated | superseded by ADR-NNNN`
- **Considered options**: only when the rejected alternatives are worth remembering
- **Consequences**: only for non-obvious downstream effects

## When to offer one

All three must be true:

1. **Hard to reverse**: changing course later costs real effort.
2. **Surprising without context**: a future reader will ask "why this way?"
3. **A real trade-off**: there were genuine alternatives and one was picked for specific reasons.

Typical fits: architectural shape, integration patterns between contexts, technology with lock-in (database, queue, auth, deploy target), boundary and scope decisions, deliberate deviations from the obvious path, constraints not visible in the code, and non-obvious rejected alternatives.
