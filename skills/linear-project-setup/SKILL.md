---
name: linear-project-setup
description: "Verify which Linear workspace is connected, then scaffold a team's projects to match a taxonomy. Use for \"set up Linear\", \"am I using the right Linear workspace\", or \"make projects for my Linear work\". Creates projects only; does not move existing issues. Not for sprints or cycles (linear-sprint-cycles) or implementing issues (issue-fleet)."
---

# Linear Project Setup

Two jobs that almost always arrive together: confirm the connector points at the workspace the user *thinks* it does, then build out the project structure they want to file work into.

Do them in that order. Projects cannot be moved between workspaces (only exported and re-imported), so a write to the wrong workspace is costly to unwind.

## Steps

### 1. Identify the connection before writing anything

Inspect the connected Linear tool schema before relying on tool or field names; the names in this file are examples. More than one Linear server can be connected, and a server's name does not tell you its workspace: run this step on each and report each one's slug, or that it errored. Write only through the one whose slug the user confirms; never fall back silently. Call the Linear "get user" tool with `me`. One call answers everything that matters:

- `name` / `email` — whose account is connected
- `teams[]` — every team they belong to, with `id` and `key`
- `isAdmin` — whether they can create teams and change settings

Then list teams for descriptions, since `get_user` omits them.

**Report the workspace slug back to the user.** Call the Linear "get workspace" tool; its `url` is `https://linear.app/<slug>`. If that tool is missing, take the slug from any issue or project `url`. The slug is how the user recognizes their own workspace; the team name alone is not enough when they have several accounts.

If the user named an expected workspace and it doesn't match, **stop and say so** rather than creating anything.

### 2. Survey what's already there

List projects and issues before adding. A fresh Linear workspace ships with onboarding issues ("Get familiar with Linear", "Import your data", "Connect your tools", "Set up your teams") — recognize these as defaults, not the user's real work, and say so. Reporting "4 issues" without that context reads as though they have work in flight.

### 3. Agree the taxonomy

Use the taxonomy already requested or established in this session. Ask only when a material choice remains unresolved. Common shapes:

- Life areas — School / Research / Personal
- Mirroring an existing folder tree the user already thinks in
- One project per active commitment, with a catch-all
- Areas as initiatives, with time-bound projects under them

Ask **one question at a time**. Do not create projects on a guess; deleting a Linear project is a destructive action you'd have to ask permission for anyway.

### 4. Create the projects

One `save_project` call each. Skip any name step 2 found, in any status; if a create errors or its outcome is unclear, list projects again before retrying. Required and easy to get wrong:

| Field | Note |
|---|---|
| `name` | Required on create |
| `addTeams` | **Required on create** (or `setTeams`) — accepts the team *name* or id. Omit it and the call fails |
| `lead` | `"me"` only when the user is the workspace's sole member; in a shared workspace, ask. Put personal areas (School, Personal) in a shared workspace only when the user confirms it |
| `icon` | Must be a name or emoji **code** (`":books:"`, `"Rocket"`) — a raw Unicode emoji is rejected |
| `summary` | Max 255 chars; shows in list views |
| `description` | Markdown, literal newlines. Use it to record what the project maps to |
| `state` | Optional. If the user already said these are active, set it on create; pass `leadTeam` too when teams have custom statuses |

Where projects mirror something on disk, name that mapping in the description (e.g. "Mirrors the vault's `School/` folder"). It's what keeps the two systems legible against each other six months later.

### 5. Report state honestly

Projects created without `state` land in the default status with no dates; surface that, since ongoing buckets look inert on the board, and offer to set a status rather than deciding for them.

Give the user the project URLs from each response.

### 6. Persist the setup

Report the workspace slug, team IDs, and project URLs. Write them elsewhere only when the user names the destination.

## Rules

- **Never delete or archive** a Linear project to "clean up" — ask first, always.
- Creating projects is a write to an external service the user owns. Fine on an explicit request; don't scaffold speculatively while doing something else.

## Gotchas

- Step 4's table holds the two most common create failures: `addTeams` omitted, and a raw emoji as `icon`.

## Untested

Multi-team workspaces. Built before 2026-09-18 against a single-team personal workspace, now retired. Not yet run against the shared RES workspace (one team as of 2026-10-05), where new projects are visible to teammates. With several teams you'll need to ask which team the projects belong to, and `addTeams` accepts more than one.
