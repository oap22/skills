# Mail Digest: the daily-note block

Read `.system/note-creation.md` before creating a missing daily note. Use
`python3 .system/scripts/daily-note.py --vault . --date <date> --ensure` from
the vault root for creation and `--region mail --body-file <digest-block>` for
the owned marker update. Re-read immediately before writing. The mail routine
owns only its mail block and its own cursor; it never stamps Linear coverage or
interview completion.

If today's note doesn't exist, create it with the helper and the documented
template contract. If it exists, touch **only** the mail block.

The block lives under its own heading directly after `## Schedule`. If the markers are missing or malformed, the helper refuses: preserve the file, keep the cursor, and report it. Do not insert markers by hand.

```markdown
## Mail

<!-- mail:start -->
*Swept 06:15 · 41 threads · 3 kept.*

**📦 Delivery** — Amazon box out for delivery today (Kingston SSD + 2 items).
**📦 Delivery** — USPS attempted 08/06, now held at Oak Creek, pickup by 08/13.
**↩️ Waiting on you** — Dr. Vance replied 08/04 re: undergrad research, 3 days unanswered.
**⚠️ Must know** — MSOE Physics I lab makeup window closes Friday 08/08.
<!-- mail:end -->
```

Nothing outside `<!-- mail:start -->` / `<!-- mail:end -->` is yours to change. The block is regenerated wholesale each run.

Include the Gmail thread link on anything he'd want to open. Keep each line to one line.
