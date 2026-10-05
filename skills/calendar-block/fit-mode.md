# Calendar Block: fit mode

The steps in `SKILL.md` assume Owen states a time. Often he doesn't: *"can you fit in the LinkedIn post"*, *"find me time for the résumé"*, *"when am I free this week?"*. The task is real, the time is the agent's problem. Same creation rules apply — only the scheduling decision changes.

## 1. Estimate the duration before looking at the calendar

Decide how long the task takes **first**, otherwise you'll shrink it to fit the first gap you see. Rough defaults:

| Shape of task | Block |
|---|---|
| Write-and-send something short (post, email, form) | 45 min |
| Review something already drafted | 30 min |
| Real focused work (résumé pass, reading, debugging) | 90 min |
| Anything with an unknown | Round **up**, don't split |

If the draft already exists, say so in the description — a 45-minute block for a task that's 80% done is a different psychological ask than a blank page.

## 2. List the day (or the range) and compute the gaps

`list_events` with `orderBy: startTime`. Then walk the sorted events and take the holes between them. Two things that are easy to get wrong:

- **`AVAILABILITY_FREE` events are not obstacles.** A block marked free is a note, not a wall.
- **A gap is not usable until you subtract transitions.** Don't start a block the same minute a soccer game ends. Leave ~15 min on either side of anything physical or off-campus.

## 3. Place it against Owen's actual shape of day

Not just "the first hole that fits."

- **Honor the wake-up wall.** The `Unavailable — sleeping in` event (`7`) is a hard floor. Nothing before it, ever.
- **Business-hours work goes in business hours.** Anything that involves another human seeing it that day — email, a call, a form with a deadline — cannot go in the 9 PM slot.
- **After the last hard commitment is a real slot,** and often the best one for low-stakes solo work. Post-game, post-practice, post-class evenings are usable if the task is light.
- **Don't wedge a 90-minute task into a 90-minute gap.** If the only fitting hole is exactly the size of the task, take the next day instead and say why.
- **Protect soccer and school.** Never place discretionary work over either, and never against a `11` (Deadlines) block.

## 4. Offer the runner-up

When booking is authorized, create **one** event and name an alternative in the report. For an availability question, return the windows without creating anything:

> "Put it at 8:45–9:30 PM, after the game. The other free window today was 4:30–6:00 PM if you'd rather not end the day on it."

This is the whole value of fit mode: he sees the shape of his own day without opening the calendar, and correcting a placed event is one click.

## 5. If nothing fits

Say the day is full and name what would have to move — don't quietly place it at 11 PM, and don't silently push it a week. "Tomorrow's first real hole is 10:15 AM; today is solid from 9:45 to 8:30 PM" is the useful answer.
