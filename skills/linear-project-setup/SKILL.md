---
name: linear-project-setup
description: Verify which Linear workspace is connected, then scaffold a team's projects to match a taxonomy. Use when the user says "set up Linear", "check my Linear connection", "am I using the right Linear workspace", "organize my Linear tasks into projects", or wants Linear projects created to mirror folders or life areas.
---

# Linear Project Setup

Two jobs that almost always arrive together: confirm the connector points at the workspace the user *thinks* it does, then build out the project structure they want to file work into.

Do them in that order. Writing projects into the wrong workspace is annoying to unwind — Linear has no bulk project move across teams.

## Steps

### 1. Identify the connection before writing anything

Call the Linear "get user" tool with `me`. One call answers everything that matters:

- `name` / `email` — whose account is connected
- `teams[]` — every team they belong to, with `id` and `key`
- `isAdmin` — whether they can create teams and change settings

Then list teams for descriptions, since `get_user` omits them.

**Report the workspace slug back to the user.** It is not in the `get_user` payload — pull it from any issue or project `url`, which looks like `https://linear.app/<slug>/issue/ABC-1/...`. The slug is how the user recognizes their own workspace; the team name alone is not enough when they have several accounts.

If the user named an expected workspace and it doesn't match, **stop and say so** rather than creating anything.

### 2. Survey what's already there

List projects and issues before adding. A fresh Linear workspace ships with onboarding issues ("Get familiar with Linear", "Import your data", "Connect your tools", "Set up your teams") — recognize these as defaults, not the user's real work, and say so. Reporting "4 issues" without that context reads as though they have work in flight.

### 3. Agree the taxonomy

Ask what the split should be before creating. Common shapes:

- Life areas — School / Research / Personal
- Mirroring an existing folder tree the user already thinks in
- One project per active commitment, with a catch-all

Ask **one question at a time**. Do not create projects on a guess; deleting a Linear project is a destructive action you'd have to ask permission for anyway.

### 4. Create the projects

One `save_project` call each. Required and easy to get wrong:

| Field | Note |
|---|---|
| `name` | Required on create |
| `addTeams` | **Required on create** — accepts the team *name* or id. Omit it and the call fails |
| `lead` | Pass `"me"` for a personal workspace |
| `icon` | Must be a name or emoji **code** (`":books:"`, `"Rocket"`) — a raw Unicode emoji is rejected |
| `summary` | Max 255 chars; shows in list views |
| `description` | Markdown, literal newlines. Use it to record what the project maps to |

Where projects mirror something on disk, name that mapping in the description (e.g. "Mirrors the vault's `School/` folder"). It's what keeps the two systems legible against each other six months later.

### 5. Report state honestly

New projects are created in **Backlog** with no start or target date. That's Linear's default, not a mistake — but surface it, since ongoing buckets sitting in Backlog look inert on the board. Offer to flip them to In Progress rather than deciding for them.

Give the user the project URLs from each response.

### 6. Persist the setup

If the harness has memory, record the workspace slug, team name and key, and the project list. Every future "add this to Linear" needs all three, and re-deriving them costs a round trip and risks filing into the wrong place.

## Rules

- **Verify before you write.** A `get_user` call is cheap; a project in the wrong team is manual cleanup.
- **The workspace slug lives in URLs**, not in the user payload. Extract it from an issue or project URL.
- **Onboarding issues are not real work.** Name them as defaults when reporting.
- **`addTeams` is mandatory on create** and is the most common failure — the error is not obvious.
- **Icons are codes, not emoji.** `":microscope:"` works, `"🔬"` does not.
- **Never delete or archive** a Linear project to "clean up" — ask first, always.
- Creating projects is a write to an external service the user owns. Fine on an explicit request; don't scaffold speculatively while doing something else.

## Untested

Multi-team workspaces. This procedure was built against a single-team personal workspace where `get_user.teams` had exactly one entry. With several teams you'll need to ask which team the projects belong to, and `addTeams` accepts more than one.
