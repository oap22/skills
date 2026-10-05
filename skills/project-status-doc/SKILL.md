---
name: project-status-doc
description: "Write a current-state document for an ongoing project from its existing notes, handoffs, and measured results, then save it to the project's folder. Use for \"status doc\", \"current state of the project\", or \"write up where we are\". Not for refreshing vault project notes from repos (project-sync), judging whether projects are still alive (vault-lifecycle), a purpose doc (vision-interview), sprint tracking in Linear (linear-sprint-cycles), or researching new sources (research-survey)."
---

# Project Status Doc

Turn the material a project already has (state notes, handoff files, measurement logs, plans) into one document that says where the project stands. It is written for teammates or an advisor who read it top-down.

## Inputs

- **Sources:** attached handoffs, project docs, and notes. Read every one before writing. If none are attached, gather the project's note, its handoffs, and the result logs in its repo, and list them in one line first. If the project is ambiguous, ask which one; if the sources hold no results or handoffs, say so before writing.
- **Destination:** the doc surface the user started from, plus the folder they named. If none is named and the project has no folder, ask. Where the workspace has its own rule for generated output (for example a vault's `Codex-outputs/`), save there and link the project note; do not edit a note or index you did not create.
- **As-of date:** today unless the user gives one.
- **Prior status doc:** if one exists, read it as a source and update it in place. Add a "Changed since <prior date>" line under Summary, and mark reversed items *superseded* with the date instead of deleting them.

## Steps

1. Read all the sources first. When a newer verified measurement conflicts with an older plan or estimate, the newer one wins; note the replaced estimate under Measured results. If the items have no dates or both are verified, keep both with their sources and list the conflict under Risks and open questions.
2. If a doc surface is available, create the doc skeleton right away: a title, an as-of date with the author, and one placeholder per section. Fill the sections one at a time so the user can watch it build.
3. Use these default sections and drop any that have nothing in them:
   - **Summary:** the lead sentence says what's decided, what's verified, what's open, the next deadline, and any decision the reader must make (with the options and a recommendation). Example: "The backbone is decided (ResNet-50), 4-GPU throughput is verified at 310 img/s, batch size is open, and the advisor draft is due 14 Oct."
   - **Direction:** the chosen approach and why, with each proposal marked decided, leaning, or open, plus approaches dropped and the result that ruled each one out.
   - **Constraints / environment:** hard rules learned by testing, written as numbered do/don't rules.
   - **Measured results:** tables with units in the headers, and a note on which figures are extrapolated.
   - **Risks and open questions:** one table with the columns risk · impact · handling.
   - **Next steps:** a checklist, with the first concrete task on top.
   - **Sources:** which handoffs or docs each part came from, with links for anything public.
4. Save a copy to the destination folder in the format the neighboring files use (for example, .docx when the other guides are Word files). Keep a markdown twin if agents will read it. If the folder has a README index, add a line for the new file.
5. Report in one or two lines: the doc link, if one was made, and the saved file path.

## Rules

- Mark every item as decided, verified, leaning, or open. Never present a proposal as a decision.
- Write or recheck the Summary last. If any risk or open item threatens the next deadline, the Summary says so.
- Label extrapolated or estimated numbers as such, and keep them apart from measured ones.
- Every fact comes from a source file or from the user. If a fact is missing, write it as an open question instead of guessing.
- Keep the document concise: lead sentences carry the point, tables hold the numbers, and there's no methodology or recap section.
- Don't add private contact details or credentials beyond what the sources already share with the same audience.

## Gotchas

- Doc exports can be large base64 blobs that are hard to move between machines. Write the markdown file directly and convert it locally (for example, with pandoc) instead of re-typing the encoded output.
- A handoff and an older plan often disagree on compute or time estimates. Check dates and let the verified figure win, or the doc will contradict itself.
