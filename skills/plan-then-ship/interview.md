# Interview

Step 2 of `SKILL.md` is not "read the repo and write the spec." It is "read the repo, then interrogate Owen until the spec could not possibly be misread" — the spec is the *output* of the interview, not a substitute for it. A weak model will execute whatever is on the page with total literalism; every sentence you didn't pin down becomes a decision the implementer makes for you, silently, and you find out at review.

## The Standard

The interview is done only when *both* of these are true, and not before:

1. **You can restate the whole spec back to Owen and he changes nothing.** Read the drafted `SPEC.md` aloud, section by section, in your own words — not "read the file" but say what it commits to. Any correction, even a small one, means you weren't done. Absorb it, rewrite the section, restate again. Loop until a full pass survives untouched.
2. **No load-bearing word is undefined.** "Handle it properly", "the usual pattern", "reasonable", "clean up", "as appropriate", "similar to the other one" — every one of these gets pinned to a function name, a file path, a line range, or an explicit behavior before it goes in the spec. If a sentence in the spec could be read two ways by someone who has never talked to Owen, ask which way.

This is the same bar `research-interview` holds for a research brief. A spec is a contract with a weaker, literal-minded model — it fails faster and more silently than a brief does, because the implementer doesn't know enough to flag its own confusion.

## The Rules That Make It Work

**One question per message. Never batch.** A list of five questions gets five shallow answers and Owen picking the easiest one to answer first. Keep the preamble short too — state what you now believe, then ask the one thing that's still open.

**Use `AskUserQuestion` when the answer space is enumerable.** Which of these two error-handling strategies, which existing file to copy the pattern from, whether a case is in scope — offer 2–4 concrete options so Owen can pick instead of type. Fall back to plain chat for open-ended threads ("what should happen if both conditions are true?") where options would anchor the answer toward whatever you happened to list. Never use the tool to pack several questions into one call — that's batching with buttons.

**Never ask what you can read.** Before the first question, read the actual files this change will touch, the surrounding module, existing tests, and any adjacent pattern Owen might mean by "like the other one." Open by *presenting what you already inferred* — the current behavior, the shape of the change, which files are involved — and ask what's wrong with it, not "what do you want."

**Follow the thread.** Each question comes from the last answer, not a fixed checklist. A hedge — "probably", "I think", "should be fine", "edge case, doesn't really matter" — is a thread. Pull it; "doesn't really matter" is where the implementer will invent something and be wrong.

**Attack the spec, don't just transcribe the request.** You are the first adversarial reviewer, before any code exists. If the requested behavior is ambiguous under a case Owen didn't mention, contradicts an existing invariant you found while reading, or the "obvious" file to touch isn't the one that actually owns the behavior, say so during the interview. That's a five-second correction now instead of a wasted implementer run later.

**Silence on a section is not agreement.** If Owen answers the goal and the edge cases but never addresses error paths or what the tests must assert, those are still open — ask them. Don't let an unanswered section default to "the implementer will figure it out."

## Ground to Cover

Every section of `spec-template.md` needs either a specific answer or an explicit call-out that it's genuinely `None`. As threads, not a script:

- **Goal** — one sentence, observable. What is true after this ships that wasn't true before?
- **Non-goals** — what's adjacent and tempting but explicitly out. If Owen doesn't volunteer these, propose the ones you'd be tempted by yourself and ask if they're in or out.
- **Files** — exact paths, not areas. "The auth stuff" is not a Touch list. If a plausible file could be touched or left alone, ask which.
- **Per-file behavior** — control flow on the happy path, in the order it happens; every edge case (empty, missing, already-exists, permission, timeout, zero, one, many); every error path (what throws, what returns, what's swallowed) named explicitly, never "handle errors."
- **What stays** — adjacent code in a touched file that looks like it wants cleanup. Ask, don't assume "while I'm here" is welcome.
- **Tests** — exact commands, exact paths, and what "passing" looks like well enough that a green run and a red run are unambiguous from the output alone.
- **Acceptance criteria** — each one observable by the reviewer without asking Owen anything further.

## Steps

### 1. Read first, then show your work

Read every file the change plausibly touches, its tests, and the nearest existing pattern for anything Owen described by analogy. Draft an inferred picture — goal, files, rough shape — and open with that, not with a blank "what do you want built."

### 2. Interview, one question at a time

Start with whatever is most load-bearing and least pinned down — usually the exact file list or the behavior on the case Owen's one-liner didn't cover. Write the answer into the draft `SPEC.md` immediately; don't hold it in conversation. If an answer implies a second question ("only when the token is expired" → "expired by clock skew tolerance, or exact `exp`?"), ask that next, not later.

### 3. Draft as you go

`.plan-then-ship/SPEC.md` is live during the interview, not written after. Long interviews get summarized by context compression; an answer that only exists in chat is an answer that can vanish. Every field in `spec-template.md` gets filled in place, including explicit `None` with a reason where nothing applies.

### 4. Run the closing loop

Read the complete spec back to Owen, section by section, in your own words. Incorporate every correction, however small, and re-read the changed sections. Repeat until one full pass changes nothing. Only then does step 3 of `SKILL.md` — the approval gate — begin; the closing loop is the interview's own check, the gate is Owen's sign-off on the artifact.

Do not let "looks fine" or "yeah go ahead" from Owen substitute for the loop actually finishing. If he waves it through before you've restated everything, restate anyway — a spec he hasn't heard back is a spec he hasn't actually approved, only tolerated.

## Rules

- **Never write `.plan-then-ship/SPEC.md`'s sections from inference alone when a question would remove the guess.** A confident guess that turns out wrong costs an implementer run and a repair loop; the question costs one message.
- **A one-line request is not a spec-ready request.** "Add rate limiting to the API" is a topic, not an answer to any of the Ground to Cover items above. Treat it as the opening move of the interview, not the brief.
- **Record what you attacked and what changed.** If you flagged a contradiction or an unhandled case during the interview and Owen's answer changed the design, that decision belongs in the spec's per-file notes so the implementer sees the reasoning, not just the conclusion.
- **"Skip" is a valid answer, but never a silent one.** If Owen explicitly says a case is out of scope, that's a Non-goal, written down. If he doesn't answer at all, that's still open — ask again before moving on.
- **Don't interview past the point of usefulness.** Once every Ground to Cover item has a specific answer or an explicit Non-goal, stop asking and move to the closing loop. Relentless means thorough, not endless.
