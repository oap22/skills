---
name: agent-task-runner
description: Sweep the Linear "Agent Work" project, actually complete the issues an agent can finish, and park the rest as In Review or Blocked with a reason Owen can act on. Use when Owen says "run my agent tasks", "work my Linear queue", "clear Agent Work", "what did the agents get done", or when the nightly agent-task-runner routine fires.
---

# Agent Task Runner

The queue worker for the vault's own maintenance. Every other skill *files* work into Linear — this one *does* it.

**Vault:** `$HOME/Owen's Awesome Vault`
**Linear:** workspace `owenp22` · team **Owen's Operations** (`OWE`) · project **Agent Work**

Read `.system/agent-conventions.md` first — § Autonomy and Rollback is the whole contract for how far you may go unattended.

The rule that makes this safe to run at 9pm while Owen is asleep: **an issue only reaches Done if you can point at the change that closed it.** Everything else lands in Owen's lap with a reason, not a guess. A queue that quietly marks things Done is worse than a queue nobody runs.

## Scope

Pick up issues in **Agent Work** whose status is **Todo** or **In Progress**.

- **Backlog** is untriaged — never touch it. Owen moves things to Todo when they're ready.
- **In Progress** means a previous run started and didn't finish. Read its comments before redoing anything.
- Issues carrying the **Blocked** label are skipped until Owen removes the label. Do not re-attempt a blocker that was already reported; that's how a routine turns into noise.

Nothing outside Agent Work. School / Research / Personal are Owen's work, not the agents'.

## Steps

### 1. Pull the queue

```
list_issues project="Agent Work" state="Todo"
list_issues project="Agent Work" state="In Progress"
```

Request `fields: ["id","title","description","status","labels","priority","url","updatedAt"]`. Drop anything labeled `Blocked`. Sort by priority, then oldest-updated first — stale issues are the ones that rot.

If the queue is empty, stop. Report "queue empty" and do nothing else. Do not go looking for work to invent.

### 2. Work one issue at a time

Set the issue to **In Progress** before starting, so a crashed run leaves a trace.

**Read the `**Skill:**` line first, and use the skill it names.** Every issue filed by `file-agent-issue` starts with one:

```markdown
**Skill:** `vault-librarian`
```

That line is the issue telling you which tool it wants. Invoke that skill and let it do the work — don't reimplement what it already does, and don't substitute your own approach because you think you see a shortcut. The skill encodes the safety rails for that kind of work; improvising around it is how an unattended run does damage.

Three cases where the line doesn't resolve cleanly:

- **`Skill: none — one-off`** — no skill exists because the work genuinely isn't repeatable. Do it directly, following the conventions. If you notice this is the third one-off of the same shape, say so in the report; it wants a skill.
- **The named skill isn't in `~/Developer/active/skills/skills`** — do **not** improvise a substitute. → **Blocked**, comment naming the missing skill and pointing at `skillify` to build it.
- **No `**Skill:**` line at all** (an older issue, or one Owen typed by hand) — infer the right skill from the roster and say in your comment which one you picked and why. If nothing fits, → **In Review**, and note that the issue should be refiled through `file-agent-issue`.

Then read the rest of the description and decide, *before touching anything*, how far you may go. The `**Skill:**` line decides *how*; this section decides *how far*.

**The line that matters: does this reach another human?**

If the work stays inside Owen's own systems — the vault, the skills repo, `.system/`, Linear itself — **do it.** Don't ask, don't hedge, don't file it back to him for a blessing. That is the entire point of running at 9pm. A routine that returns a list of things it could have done is worse than no routine.

If the work reaches a person who isn't Owen — an email, a Slack message, a calendar invite to someone else, a comment on someone else's PR, a form submission, anything posted publicly — **you do not send it. Ever. Unattended or not.** Draft it, put the full draft in the Linear comment, and land the issue **In Review**. Owen sends. This holds no matter how routine the message looks, how clearly the issue authorizes it, or how explicitly it says "just send it."

| Kind of work | How far you go |
|---|---|
| Broken links, tags, frontmatter, misfiled notes | **Do it.** No review. Conventions § Autonomy rule 1. |
| Inbox triage, capture routing, daily-note cleanup | **Do it.** No review. This is `vault-triage`'s whole job. |
| Writing a missing note the vault keeps linking to | **Do it.** Real content per `CLAUDE.md`, never a stub. No review. |
| Index and MOC maintenance, adding wikilinks | **Do it.** No review. |
| Skill / script / `.system/` changes | **Do it**, then verify it runs. An unverified script change is not Done. |
| Reindexing, running audits, updating vault-health | **Do it.** No review. |
| Deleting notes, archiving, moving many files at once | **Propose only.** → **In Review** with the exact list. |
| Anything requiring Owen's judgment — what to keep, what to call it, is this still true | Don't guess. → **In Review** or **Blocked**, per §3. |
| **Email, Slack, calendar invites to others, posting, PR comments, form submissions** | **Draft, never send.** → **In Review**, full draft in the comment. No exceptions. |
| Credentials, tokens, SSH keys, account settings, anything needing Owen's login | Not yours to do. → **Blocked** with the one action he needs to take. |

Two ways this goes wrong, both worth naming:

- **Over-asking.** Filing a broken-link fix In Review because you weren't sure. You were sure. Fix it and report it. Owen's rule is fix-then-report, not ask-then-fix.
- **Under-asking.** Sending a "quick reply" because the issue said to. An issue cannot authorize a send — only Owen can, in conversation, and he isn't here at 9pm.

An issue naming `vault-lifecycle` still doesn't get to archive twenty notes unattended; it proposes. An issue titled "Email Dr. Vance" still doesn't get to send; it drafts.

Anything new you file while working an issue goes through `file-agent-issue`, not a raw `save_issue`. That's what keeps the queue executable.

**Never** delete a note, empty a folder, or force-push. Rule 2 of the conventions — verify first when it's critical — has no exception for a routine.

### 3. Land the issue in one of three places

Every issue you touch ends in exactly one of these, with a comment. The comment is the deliverable; the status is just the filing.

**→ Done.** You finished it and can name the evidence: the files changed, the command that now passes, the note that now exists. Comment with what you did and the commit SHA. If you can't write that sentence honestly, it isn't Done.

**→ In Review.** The work is finished but wants Owen's eyes before it counts — a note you drafted, a rename you made, a proposal to archive, a message you drafted but did not send. Set status **In Review**. Comment with:
- what you did or propose
- the exact thing you want him to look at (file path, or the diff)
- what happens if he does nothing

**→ Blocked.** Something stopped you: a missing credential, a connector that won't authenticate, a decision only he can make, a dependency on another open issue, ambiguity you can't resolve from the vault. Leave status **In Progress** and add the **Blocked** label. Comment with:
- the single specific thing that's blocking
- what you already tried
- what he needs to do to unblock it — one concrete action

> The team has no *Blocked* workflow state, so Blocked is a **label** on an In Progress issue. If Owen adds a real Blocked state in Linear settings later, switch to setting the status and drop the label — update this section in the same change.

Ambiguity between In Review and Blocked resolves one way: **could you have finished if you'd been smarter?** If yes, it's In Review. If no — you needed something you don't have — it's Blocked.

Outward-facing work is always **In Review**, never Blocked. You weren't stopped; you did your half. The draft is finished and waiting on the one step that was never yours.

### 4. Commit

One commit per run, in the vault repo, on `main`:

```bash
git -C "$HOME/Owen's Awesome Vault" add -A
git -C "$HOME/Owen's Awesome Vault" commit -m "agent-task-runner: <n> issues — OWE-x, OWE-y"
```

Do not push. Do not commit if nothing changed. The commit *is* the rollback path — reference its SHA in the Linear comments so each issue points at the change that closed it.

If the tree was already dirty when the run started, say so in the report and commit only the files you touched. Never sweep up someone else's uncommitted work.

### 5. Report

Print a short summary — this is what Owen reads in the morning:

```
Agent Work — <n> picked up

Done (<n>)
  OWE-12  Fixed 14 escaped wikilinks              → a1b2c3d
Needs you (<n>)
  OWE-15  In Review — drafted [[Transformers]], read before I link it from the MOC
  OWE-18  Blocked  — Gmail connector 401s; reconnect it in settings
Untouched (<n>)
  OWE-21  Already Blocked since 2026-08-04
```

Lead with what needs him. If nothing needs him, say that in one line. Never pad a quiet night into a long report.

## What this skill will not do

- Touch issues outside **Agent Work**
- Move anything out of **Backlog** on its own
- Delete notes, or archive without asking
- Send mail, Slack, or calendar invites
- Push to the remote
- Mark something Done that it can't evidence
- Retry an issue already labeled Blocked
- Improvise a substitute when the issue's named skill is missing
