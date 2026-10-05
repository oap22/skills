# Mail Digest: scheduling

**Local** scheduled task, never a cloud routine — a cloud agent can reach neither Gmail nor the vault and fails silently every morning. See the `local-routine` skill.

Live routine: `mail-digest`, `15 6 * * *` America/Chicago — fifteen minutes ahead of `morning-interview` (`30 6 * * *`), so the mail block is already in the note when the interview renders and Owen can be asked about what's in it.

The two tasks share the daily note and don't collide because each owns disjoint markers — this one owns `<!-- mail:* -->`; `daily-note` owns `<!-- linear:* -->` (rendered during the interview routine); `morning-interview` owns `<!-- interview:* -->`. All create the note from the same template if missing. **Never widen any write scope.**
