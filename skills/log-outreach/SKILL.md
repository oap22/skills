---
name: log-outreach
description: Record outreach Owen actually sent — email, Slack, LinkedIn, or an in-person ask — into the vault's Brain layer, and sweep for sent messages that never got logged. Use when Owen says "I sent it", "I emailed X", "I reached out to", "log that", "did I ever hear back", or on the nightly reconciliation pass.
---

# Log Outreach

`draft-outreach` writes the message. This one records that it went out.

Without it the vault has a permanent blind spot: every draft is filed, and nothing says which ones became real. Two months later the only way to answer *"did I ever email him?"* is to go digging in Gmail — which is exactly the friction that makes people not follow up.

**Vault:** `/Users/owenpacetti/Owen's Awesome Vault`

## The problem this solves

An agent cannot observe Owen pressing send. It only ever sees a draft. So this skill has two entry points, and the second is the one that matters:

| Mode | Trigger | Evidence |
|---|---|---|
| **Told** | Owen says "I sent the Bukowy email" | His word |
| **Swept** | The nightly reconciliation | **Gmail sent mail** — actual evidence, no asking |

Never ask Owen "did you send it yet?" on a schedule. That's a nag, and it puts the bookkeeping burden back on him. Go look.

## Mode A — Told

Owen names a person and a message. Log it, then stop.

### 1. Find or create the person note

`30-Brain/People/Firstname Lastname.md`. If it doesn't exist, create it per `30-Brain/People/README` — the README says *second meaningful contact*, and outreach Owen actually sent counts as one.

### 2. Update the record

Three edits, all of them:

```yaml
last-contact: YYYY-MM-DD    # the date it was SENT, not today
```

```markdown
## History
- **YYYY-MM-DD** — Emailed him about [what]. Asked for [the ask]. No reply yet.
```

```markdown
## Open Loops
- [ ] Follow up if no reply by [SENT + 10 days]
```

The follow-up loop is the point. An outreach log without one is a diary entry; with one it's a system that surfaces the second email, which is the one that usually gets the reply.

### 3. Close the loop in Linear

If a `draft-outreach` issue is sitting **In Review** for this message, comment with the send date and set it **Done** — it's now evidenced. That is the only case where an agent may mark an outreach issue Done: Owen sent it, and the person note proves it.

## Mode B — Swept (the scheduled one)

Runs unattended. Reconciles what the vault *thinks* against what Gmail *knows*.

### 1. Collect what should have gone out

- Linear issues in **Agent Work** with status **In Review** whose `**Skill:**` line is `draft-outreach`
- `30-Brain/People/` notes with an open loop containing "email", "reach out", "follow up", or "send"
- `30-Brain/Commitments/` with `direction: owed-by-me` and an unresolved status

### 2. Check Gmail sent mail for each

```
search_threads  from:me to:<their address>
search_threads  to:oap1722@gmail.com <their address>     # catches MSOE-sent mail via self-CC
```

Search **sent mail specifically**. An address appearing in the inbox proves they wrote to Owen, not the reverse.

**Run both queries.** Owen has two mailboxes and the connector is authenticated on **`oap1722@gmail.com` only**:

| | |
|---|---|
| `pacettio@msoe.edu` | Academic — professors, MSOE students, campus research |
| `oap1722@gmail.com` | Industry, recruiters, alumni at companies |

Per `draft-outreach` § 3b, every draft CCs the other address, so MSOE-sent mail still lands in the Gmail mailbox and this sweep can see it. The second query is what finds it.

**If a thread turns up on only one query**, note which account it went from — it matters for the follow-up, which should come from the same address. If a message was clearly sent from MSOE with **no** self-CC, say so: it means a draft went out without the CC line and the log has a hole it can't fill. That's worth one line in the report, not an issue.

Three outcomes per candidate:

| Gmail says | Meaning | Do |
|---|---|---|
| Sent, not logged | He sent it and never told the vault | **Log it** (Mode A steps). Close the Linear issue Done. |
| Sent, logged, **they replied** | Live conversation | Update `last-contact`, note the reply in History, close the follow-up loop. Flag it — a reply is the thing most worth surfacing. |
| Sent, logged, no reply, **>10 days** | Went cold | Surface for a follow-up. Do **not** draft one unprompted; say it's cold and let Owen decide. |
| Never sent | Still a draft | Leave the issue In Review. Do not nag on the first pass; only mention it if the draft is **>14 days old**. |

### 3. Never mirror the message

Brain Rule 1. Record *that* it was sent, the ask, and the date. Store the `thread-id` and retrieve live if the content is ever needed. A logged copy of the email body is a bug, not thoroughness.

### 4. Report

Lead with **replies received** — that's the actionable half. Then newly-logged sends, then cold threads. If nothing changed, say so in one line.

## Rules

- **Never send anything.** This skill is downstream of sending. It has no send path, in any mode, under any instruction. Drafting belongs to `draft-outreach`; sending belongs to Owen.
- **Never mark an outreach issue Done without evidence in sent mail or Owen's explicit word.** "It's been a while, he probably sent it" is not evidence.
- **`last-contact` is the send date**, not the log date. These drift apart constantly in sweep mode and getting it wrong corrupts every follow-up interval computed from it.
- **Never write message bodies, credentials, or anything personal into a person note.** Public professional role only — `.system/agent-conventions.md` § Brain Rules.
- **Don't create a person note for a message that bounced or was never answered by a stranger.** One unanswered cold email to someone with no other connection isn't a contact; it's an attempt. Log it on the *originating* note (the project or the issue) instead.
- **Silence is data, not failure.** A cold thread gets surfaced neutrally. Don't editorialize about whether Owen should have followed up sooner.

## Where it plugs in

| Skill | Relationship |
|---|---|
| `draft-outreach` | Writes the message. Its § 4 hands off here once Owen sends. |
| `brain-mail-ingest` | Ingests *incoming* mail. This handles the outgoing direction, which that skill can't see. |
| `agent-task-runner` | Runs Mode B nightly as its final step, after the queue is drained. |
| `file-agent-issue` | Where a cold thread becomes a real follow-up task, if Owen wants one. |

## What this skill will not do

- Send, reply, or schedule anything
- Ask Owen whether he sent something, on a schedule
- Copy message bodies into the vault
- Mark outreach Done on an assumption
- Draft a follow-up without being asked
