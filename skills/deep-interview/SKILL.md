---
name: deep-interview
description: Interview Owen one question at a time to build or extend his profile in the vault, reading what's already known first and writing answers down as they come. Use when he says "interview me", "ask me about myself", "build my profile", "update my profile", "deep interview", or wants the vault to hold a real picture of his situation rather than fragments.
---

# Deep Interview

Build a picture of the user's actual situation — one that makes every other skill smarter — by asking, not guessing.

**Destination:** `05-Profile/Owen.md` in the vault. Extend it; never start a fresh file when one exists.

## The Rules That Make It Work

**One question per message. Never batch.** This is the single most important rule. A numbered list of six questions gets six shallow answers; one question gets a real one. Keep the text around the question short too — a long preamble recreates the problem.

**Never ask what you can read.** Before the first question, read the profile, `CLAUDE.md`, the project notes, `School/`, daily notes, and any reflections. Open by *presenting what you already believe to be true* and inviting correction. It respects their time and it surfaces errors that a question wouldn't.

**Follow the thread.** Each question should come from the last answer, not from a prepared list. "I was working" → what's the job → when did it end → what's next → who do you know. A script cannot find the thing you didn't know to ask about.

## Steps

### 1. Read first, then show your work

Read everything relevant, then present the inferred picture as a table and ask them to correct it rather than repeat it. Flag any contradictions found in the vault — a note tagged `spring` sitting in a `Fall/` folder is a real question.

### 2. Ask, one at a time

Start with the most load-bearing unknown, usually identity or direction. Let each answer choose the next question.

Areas worth reaching eventually — as threads, not a checklist: program and standing · direction and what they'd work on for a decade · work history · what's live and time-critical · commitments and real weekly hours · priorities and what's non-negotiable · energy, focus, and what actually refills them · health · money as it constrains choices · who's in their corner · and finally, how they want *you* to operate.

### 3. Do arithmetic on the answers

The highest-value output is usually a number they haven't computed. Practice hours plus travel plus game days. Sleep needed minus sleep gotten, times seven. Days between now and the thing that consumes the calendar.

Turn "it's a lot" into "18–23 hours a week," and "I'm tired" into "a 14-hour weekly deficit." That's what converts a conversation into something actionable.

### 4. Reflect patterns back

Say what the answers add up to, especially when they haven't named it:

- A README that already states the thesis they just described out loud
- A stall pattern visible across repos — big builds stopping partway, not dying early
- Every listed hobby being either training or work, with no recovery in it
- A contact whose job is the exact intersection of everything they want

Be factual, not flattering. And when they correct the inference, say so plainly and move on — a wrong pattern named and dropped costs nothing; one defended costs trust.

### 5. Write as you go

Write to the profile **during** the interview, not at the end. Long conversations get compressed, and unwritten answers are lost answers. Keep a `## Still Open` section listing what hasn't been covered, and prune it as you go.

### 6. Fix what the interview reveals

Answers routinely expose errors elsewhere. Correct them at the source — a mis-tagged course note, a misattributed document, a duplicate person note, a name recorded wrong. An interview that only writes one file is leaving value behind.

### 7. Close on the working relationship

The last question should be about how they want you to operate — autonomy, when to verify, how much to flag unprompted. Save the answer as durable guidance, not just a profile line.

## Rules

- **Verify proper nouns against written sources.** Owen dictates; names arrive garbled. A repo namespace, author list, or email beats a spoken name. Confirm rather than silently correcting.
- **State a number once.** Flagging the same urgent finding four times reads as nagging and buries everything else. Say it precisely, record it, move on.
- **"Skip" is a valid answer.** Ask about money, health, and family plainly, but drop them without friction.
- **Don't turn it into advice.** One or two lines of implication is right; a plan is a different task and derails the interview.
- **Don't flatter.** "That's a strong package for your class year, here's why" is useful; "wow, impressive" is noise. Understatement from them is worth correcting with evidence.
- **Record hedges as hedges.** "I think it counts for credit" gets written down as unconfirmed, with a note to check.

## Environment

- zsh aborts on non-matching globs — a `for f in dir/*.md` loop dies if the directory is empty. Use `find | while read`.
- `ls` is aliased to a git-aware tool that hangs in large or fresh repos. Use `/bin/ls`.
