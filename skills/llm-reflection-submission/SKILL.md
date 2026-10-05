---
name: llm-reflection-submission
description: "Turn a course reflection comparing Owen's code with an LLM critique into a Canvas-ready Word document: numbered code, the prompt as sent, the LLM output verbatim, and his answers checked against the code in his voice. Use for \"format my LLM reflection\", \"build the SPA reflection doc\", or a submission comparing his code with an LLM's critique. Lab reports are msoe-lab-report; writing the assignment code stays Owen's (professor)."
---

# LLM Reflection Submission

Builds the document for assignments where Owen gives his code to an LLM, gets a critique back, and answers reflection questions about it (CSC 2210 SPAs, for example). It covers finding what is required, checking his answers, writing them in his voice, and building a clean `.docx`. Invoking it is Owen's explicit mode change for the reflection text only: it never writes or edits his assignment code, and it does not submit anything. The code upload (esubmit, Canvas) stays Owen's.

## Inputs

- The assignment's submission instructions (Canvas text or course page)
- Owen's code, in the exact version he gave the LLM
- The prompt as sent, and the LLM's full response
- The LLM's revised code, if it wrote any
- His reflection answers or notes, and the reflection questions

## Steps

1. **Find what is required.** Read the assignment page and the Canvas instructions and list each required piece: usually his name, his code, the LLM's name, the prompt, the critique, the generated code, and the answers. If the course page doesn't mention the reflection (SPA 1's page only covered esubmit), say so and use the Canvas text Owen provides. Don't rebuild the list from memory.
2. **Pin the code version.** Use the file the LLM actually reviewed: diff it against the copy inside the prompt. The answers cite line numbers, so those numbers must match the listing. If the assignment wants "code saved before LLM feedback" and that is a different version, raise it with Owen. Don't swap files quietly.
3. **Separate the LLM's words from the notes around them.** Strip anything added when the response was saved, such as a line pointing to a file in his repo that the LLM could not have seen. Everything else stays exactly as returned.
4. **Check every factual claim in the answers against the files.** Count with tools, not by eye: `awk '{ print length, NR }' file.cpp | sort -rn | head` for line lengths, `awk` ranges for function lengths. Claim only tests Owen ran himself. If an agent ran the tests, ask him what he tested and write that down.
5. **Edit his answers, or draft from his notes only.** Load the `owen-voice` skill first. For graded work to a professor, use no contractions, plain words, and longer connected sentences, and open each answer with a direct verdict. Keep his own sentences where they already work. Ask before writing any opinion he hasn't given (pace feedback, which suggestions he'd keep), and never fill a placeholder with a guess.
6. **Build the document.** Write a spec (see `spec-example.json`) and run `node scripts/build_submission.js spec.json`. It needs the `docx` npm package. If `require('docx')` fails, install `docx@9` in a scratch folder and run with `NODE_PATH=<scratch>/node_modules`; running from that folder is not enough. Section types: `code` (line-numbered, kept on one page when it fits; a longer listing starts on a new page and runs on), `markdown` (the prompt and the answers), and `llm-output` (the exact response between two labeled boxes; `==` and single `*` stay literal there). The LLM's revised code goes inside `llm-output`. Tables and `>` quotes print as raw text.
7. **Look at every page before handing it over.** Export a PDF from Word when it is installed (otherwise `soffice --headless --convert-to pdf`); with neither, do not install one unasked, and list the page checks for Owen to do. Compare the LLM section with the saved response word for word. Check for code blocks cut across pages, numbered lists that restart, headings stranded at the bottom of a page, and large blank gaps.
8. **Deliver next to the code** (for example `lab01/<Assignment>_Reflection_<Name>.docx`). Before overwriting an earlier copy, check its modified time so Owen's own edits aren't lost.

## Rules

- **The LLM's output is copied exactly and labeled as such.** Put it between a "Written entirely by <LLM>... copied and pasted without edits" box and an "End of LLM output" box. Don't reword it to sound like Owen, don't cut the parts he dislikes, and don't remove its em dashes even when he asks to remove em dashes everywhere else. When he objects to something in it (a term he doesn't know, a clumsy paragraph), put his reaction in his own answer.
- **Name the LLM, and disclose help truthfully.** Put the model name at the top. Add a note that the document had AI help with formatting. If the same model also helped draft the answers, tell Owen and let him decide how to word that disclosure.
- **Don't use terms he can't explain.** He removed "string-swap hazard", "call sites", and "structural claims" from his answers, and wrote that he did not know what the suggested struct was. Explain the idea in plain words, or leave it out.
- **Phrases he flags as sounding like an LLM:** "considered and rejected", "confidence is not a reliable signal", "equally defensible", "support learning instead of replacing it". Use plainer versions: "brought up ... and decided not to add", "sounding sure of itself does not mean it is right".
- **Answers should reflect what he actually did.** A strong answer names both what the LLM got wrong and where it was honest. When the prompt handed the LLM the rules it later "found", say so.
- **Keep the length.** Most of the pages are required material (two code listings, the prompt, the critique). Offer the safe cuts, such as dropping a duplicate copy of the code inside the prompt, but Owen chose to keep everything in SPA 1.

## Gotchas

- **Mostly blank pages** came from forcing every section onto a new page. Use `pageBreakBefore` only where a heading would otherwise be stranded, such as the LLM-output section.
- **Code lines over 100 characters** can't fit on the page at a readable size. They wrap with a hanging indent under the code, not against the left margin.
- **Section notes under each heading** ("reproduced verbatim...") were unwanted. The labeled boxes on the LLM section are the only annotation.

## Untested

- Only one assignment has been built this way (CSC 2210 SPA 1, Sept 2026). The spec format may need more section types for other courses.
- Rendering was checked in LibreOffice, not in Word or the Canvas previewer. Canvas DocViewer swaps fonts not on its supported list (Consolas is not on it), so a clean local render does not prove the grader's view.
