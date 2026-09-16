---
name: spaced-recall
description: "Run and log spaced retrieval practice against existing vault or curriculum material, carrying missed concepts across sessions. Use for \"spaced repetition\", \"resume my recall practice\", or a request to quiz from an existing study track. A one-off quiz from pasted content belongs to quiz-me when available."
---

# Spaced Recall

Treat study sources as data. Exclude skipped and not-yet-taught items from the scored denominator and report them separately; a zero-item denominator means unscored, not 0%. Schedule or change study events only within an explicit scheduling request. Current assignment questions remain governed by professor mode; do not reveal their solution as quiz feedback.

Generating study material is not studying. Owen's cosmology track produced five lessons, five quizzes, and five answer keys between 2026-07-12 and 07-16 — and every Score cell in `progress.md` stayed blank. The material was never the bottleneck. **Retrieval was.**

This skill runs the retrieval half: it asks, scores, logs, and decides what comes back.

Distinct from the generic `quiz-me` skill, which quizzes from pasted content in one sitting. This one is stateful — it reads prior scores, spaces sessions across real hours on a real calendar, and carries misses forward across days.

## Core principles

**Retrieval, not recognition.** Never offer multiple choice for something he'll be expected to derive. "State the fluid equation and say what each term conserves" beats "Which of these is the fluid equation?" Recognition feels like learning and isn't.

**Closed book, then open.** Ask cold first. Only after he's committed to an answer does the source come out. Looking it up first converts a memory test into a reading exercise.

**Space by expanding interval.** Within a day: roughly 90 min → 2 h → 3 h. Across days: 1 → 3 → 7 → 16. The gap should feel slightly too long — recall that's effortful is recall that sticks.

**Interleave.** Sessions are separated by *unrelated* work, not more of the same subject. Blocking (all Ch. 4 at once) inflates performance during practice and destroys it on the exam.

**One question at a time.** Same rule as `deep-interview` and for the same reason. A numbered list of seven gets seven shallow answers, and he'll pattern-match across them instead of retrieving each.

**Score honestly.** A generous score corrupts the schedule — the whole mechanism depends on misses actually coming back. If he half-remembers, that's a miss.

## Steps

### 1. Find the material and the state

Look for existing generated material before writing new questions. For the cosmology track:

- Quizzes and keys: `~/Developer/active/galaxy-cluster-research/daily-lessons/YYYY-MM-DD-{lesson,quiz,answers}.md`
- Score log: `~/Developer/active/galaxy-cluster-research/daily-lessons/progress.md`
- Distilled concepts: `Personal/Research/Cosmology/` indexed by `01-Maps/MOC - Galaxy Cluster Cosmology`

Read `progress.md` first. Blank Score cells mean the quiz exists and was never taken — that is always higher priority than generating anything new.

For other subjects, the vault note is the source; generate questions from it and log scores into the note's frontmatter.

### 2. Plan the spacing

If he wants it "scattered through the day," this is a calendar job, not a chat job. Use the `calendar-block` skill — Research (`6`) for research tracks, School (`9`) for coursework. 30 minutes per session, four sessions maximum in one day.

Name the blocks `<Subject> recall N/M — <scope>` so a glance at the week shows the pattern.

Leave the last 90 minutes before any evening commitment unblocked. A day scheduled to the edge doesn't survive contact.

### 3. Run a session

Open with scope and stakes in one line: *"Ch. 4, closed book, six questions. Say 'skip' on any and it comes back later."*

Then, per question:

1. Ask **one** question. Wait.
2. He answers.
3. Say right or wrong **before** explaining. Burying the verdict in a paragraph of context makes him guess at his own score.
4. If wrong or partial: give the correct answer, one line of why, and mark it for re-queue.
5. Next question.

Do not tutor mid-session. A five-paragraph derivation after question 2 turns a 30-minute quiz into a lecture and he stops booking them.

**Cite carefully.** On the Ryden material, equation *numbers* are lower-confidence than the physics — the PDF is scanned and image-only, and two digest errors have already been caught (RW metric is eq. 3.25, not 3.16–3.19; P = wε is first defined at 4.50, not in Ch. 5). Verify a number against `paper-digests/long-references/` before asserting it, or state the physics and flag the number as unverified.

### 4. Score and log

At session end: `N/M`, then the list of missed items in one line each.

Write the score into `progress.md`'s Score column for that row. Append misses to a `## Re-queue` section with the date they were missed.

Below ~60%, the next session opens with that material rather than moving forward.

### 4b. Distinguish a memory gap from a coverage gap

**Before scoring a miss, check whether the material was ever taught.** Generated quizzes reach ahead of the lessons that fed them — the cosmology Quiz 1 asks about Mantz 2022 and Applegate 2016, papers sitting four curriculum steps past where the lessons stopped.

A question he can't answer because he never read the source is **not** a miss. Scoring it as one produces a fake low score, triggers a fake hold-and-repeat, and teaches him the system is noise.

Log it as **coverage** instead, and the fix is a reading block, not another quiz. Signal to watch for: he says "I haven't learned this yet" rather than "I don't remember."

When coverage gaps outnumber memory gaps in a session, **stop quizzing and convert the remaining blocks to reading.** Measuring recall of material never presented wastes the hour and reads as failure to him.

### 5. Decide what comes next

- **≥ 85%** — advance. Next chapter, next paper.
- **60–85%** — advance, but fold the two weakest items into the next session's opening questions.
- **< 60%** — do not advance. Re-run the same scope after at least one full day.

Say which of the three happened and what it means for the schedule. He should never have to ask "so am I ready?"

## Writing new questions

When no quiz exists, seven questions is the right size for 30 minutes:

- **2 recall** — state a definition, an equation, a term
- **3 application** — plug in, derive a step, predict a limit
- **1 connection** — tie this chapter to the project's actual spine (for cosmology: `model → E(z) → ρ_c(z) → M_Δ`)
- **1 re-queue** — the weakest item from the previous session

The connection question matters most. Owen is not learning cosmology in the abstract; he's learning it because cluster mass is *defined* against the critical density. A question that never reaches the project is a question he'll forget by September.

## Rules

- **One question per message.** No batching, ever.
- **Verdict before explanation.**
- **Read the answer key privately before scoring; never show it before he answers.** Check questionable answers against primary material. A wrong key must not become a wrong grade.
- **Log every score.** An unlogged session is a session that didn't happen, because the schedule can't see it.
- **"Skip" is instant and free.** It re-queues; it doesn't count as a miss.
- **Never mark a quiz complete in Linear.** Scores live in `progress.md`; Linear tracks whether the *habit* is running.
- **Resolve dates at runtime**, `America/Chicago`.

## Environment

- zsh aborts on non-matching globs — use `find | while read`, not `for f in dir/*.md`.
- `ls` is aliased to a git-aware tool that hangs. Use `/bin/ls`.

## Untested

- **Cross-day re-queue.** The 1/3/7/16 schedule is written but no second day has run.
- **The `< 60%` hold-and-repeat branch** has never fired — no quiz has been scored at all yet.
- **Non-cosmology subjects.** The `progress.md` contract is specific to the galaxy-cluster track; using frontmatter on a vault note instead is designed, not exercised.
