---
name: resume-build
description: Rebuild or re-tailor Owen's resume — interview for what's new, mine the vault and local repos for evidence, apply career-center conventions, and compile the Typst source to a verified one-page PDF. Use when he says "update my resume", "work on my resume", "tailor my resume", "add this to my resume", "resume for this application", or when new experience lands that the resume doesn't reflect.
---

# Resume Build

Owen's resume is a Typst document at `~/Developer/resume/resume.typ`, compiled to
`Owen-Pacetti-Resume.pdf`. This skill rebuilds it, re-tailors it for a posting, or folds in new
experience — then digests what was learned back into the vault.

Conventions live in `~/Owen's Awesome Vault/03-Areas/career-recruiting.md`. **Read that first** —
it holds the career-center rules (CMU SCS, Harvard) that drive every formatting decision, so they
don't get re-derived from web searches that surface resume-SaaS marketing content.

## Steps

1. **Read the current state.** `~/Developer/resume/resume.typ`, plus
   `02-Projects/Resume-2026.md` and `03-Areas/career-recruiting.md` in the vault.

2. **Mine the vault before asking anything.** `05-Profile/Owen.md` holds academics, work history,
   direction, and network. `02-Projects/*.md` holds every project with status and commit counts.
   `School/Sophomore/*/` holds current coursework. Most interview answers are already written down —
   asking for them wastes his time and signals the vault isn't being used.

3. **Interview for the gaps only — one question at a time.** Never batch. Ask, wait, follow up.
   Target what the vault can't know: what shipped, what the numbers were, what ended, what's next.
   Verify anything the vault asserts that looks stale rather than trusting it.

4. **Verify every skill claim against real evidence.** Check `requirements.txt`, `pyproject.toml`,
   and actual imports in the repos. Then apply the honesty rule below.

5. **Draft the content**, then compile:
   ```bash
   cd ~/Developer/resume && typst compile resume.typ "Owen-Pacetti-Resume.pdf"
   ```
   Mark any unresolved fact with `⟨ANGLE BRACKETS⟩` so it is impossible to miss in the rendered PDF.
   Grep for `⟨` before declaring done.

6. **Force it onto one page by cutting words, not type size.** Render and read it:
   ```bash
   typst compile resume.typ preview.png --ppi 120
   ```
   Then look at the PNG. Fix orphan lines — a bullet that wraps for two words wastes a whole line.

7. **Verify ATS parseability by extraction, never by appearance:**
   ```bash
   python3 -c "import pypdf; print(pypdf.PdfReader('Owen-Pacetti-Resume.pdf').pages[0].extract_text())"
   ```
   Read the output in order. Every section header present, no scrambling. This is the failure mode
   that silently kills resumes.

8. **Digest back into the vault.** Update `02-Projects/Resume-2026.md` with what changed and why.
   Add durable conventions to `03-Areas/career-recruiting.md`. **Correct any vault facts the
   interview proved wrong** — say so explicitly rather than editing silently.

9. **Deliver the PDF** to Owen and report what changed, what was cut, and what remains open.

## Rules

- **Never claim a skill on repo evidence alone.** A library in `pyproject.toml` proves the repo uses
  it, not that Owen can defend it in an interview. He had PyTorch and TensorFlow removed on
  2026-08-07 for exactly this reason — the work was largely agent-written. Ask before claiming, and
  accept "no" without arguing. An unbackable skill is a liability, not an asset.
- **Coursework he is enrolled in but has not started is not evidence of a skill.** Listing the
  course is fine; listing its libraries as skills is not.
- **One page.** Under 10 years of experience means one page. This is the constraint that forces
  every other decision — when something must go, cut, don't shrink.
- **Bullets: Action Verb + Context + Result.** Past tense unless ongoing. One line where possible,
  never more than two.
- **Research is not employment.** It gets its own `Research Experience` section — which is also what
  lets the strongest material sit near the top honestly.
- **Papers under review still count.** Cite properly and mark `under review`.
- **Skip the summary** unless tailoring to a specific posting. A summary naming three target roles
  is worse than none.
- **Dates must be true.** Check whether a role *ended*; "Present" on finished work is a real error.
  This session caught the digital twin research listed as ongoing when it ended May 2026.
- Older `.docx` resumes in `~/resumes/` and `~/Documents/resumes/` are superseded — never edit them.
  The `resume.pdf` in `~/Developer/personal-website/` is a 610-byte placeholder, not a real resume.

## Failure Modes Hit Before

- **`typst` not installed** → `brew install typst`.
- **First compile ran two pages.** Fixed by tightening prose so bullets stop wrapping — not by
  reducing font size. After it fits, spend the reclaimed space back on leading and section gaps;
  a cramped one-pager is worse than a breathing one.
- **Fetching a career-center PDF from the web returned binary garbage.** The fetch tool saves the
  file locally regardless — extract it with `pypdf` instead of re-fetching.
- **Vault held stale facts** — a GPA estimate that was wrong, a project misattributed to a research
  group, a stale degree program. Verify with Owen; correct the source notes, don't just work around.
- **Voice dictation garbles numbers.** "It was 2:00, and they gated probably around 12:00" meant
  2 permission levels and 12 utilities. Restate the interpretation before building on it.
