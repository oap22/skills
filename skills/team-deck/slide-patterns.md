# Slide patterns

How each kind of content became a picture in the v2 decks (4 Oct 2026). Pick the row that fits, then keep the words inside the budget in [SKILL.md](SKILL.md#rules).

| Content | Visual | Example from v2 |
|---|---|---|
| A training curve or score over steps | Line chart, one panel per seed, dashed baseline for random play | Held-out score at 400k, 1M, 2M for seeds 2, 3, 4; random = −20.26 |
| How far each run got | Horizontal bar per seed, marked where it stopped | Seeds 0 and 1 died early; seeds 3 and 4 reached 2M |
| A headline result | 2 or 3 big numbers with a short label under each | Best held-out score, games won of 100, frames trained |
| Real vs imagined play | The open_loop GIF, with row labels REAL / DREAM / ERROR beside it | Untrained GIF next to the 1M-frame GIF |
| A process (how a cycle works, how an agent does a task) | Icon flow: boxes with arrows, one or two words per box | 7-step agent flow; issue status flow |
| A time period | Timeline bar with the dates on it | The two-week cycle |
| Load per person | Bar per person against the budget line | Points per person vs the 6-point budget |
| A set of docs or files | Tree diagram from the entry file, source of truth in an accent color | `AGENTS.md` → research-state, setup, linear, … |
| A list of tools or skills | Grid of tiles, name only | The 9 repo skills |
| Next steps or a plan | Roadmap with lanes and milestone lines, issue keys as the only text | Oct to Feb roadmap |
| A decision for the meeting | One question, 2 or 3 option tiles | Cycle 1 is over budget: cut what? |
| Data not there yet | Dashed empty frame, labelled with run ID and what goes in it | Seed 5, 6, 7 GIF frames; `[ ]` number cells |

## Footer line

Each data slide has one small footer with the source: issue key, job IDs, or a repo path. This keeps the slide clean and still lets anyone check a number.

## Speaker notes

One or two sentences: what to look at, and why it matters. Example: "Watch where the dream row stops matching the real row. That moment is what we will measure."
