# Interview and spec approval

Read the relevant repository code, tests, and current guidance before asking questions. Fill `spec-template.md` using the request and established project patterns. Decide routine file placement, existing conventions, and reversible implementation details yourself; record assumptions that affect behavior.

Ask one question at a time only when an unresolved choice materially changes user-visible behavior, scope, compatibility, cost, or acceptance criteria. Answered questions stay answered. A short request can be sufficient when its behavior is clear from the code and context.

Draft `.plan-then-ship/SPEC.md` as the decisions become concrete. Include observable acceptance criteria, ownership, and relevant tests. Mark a section `None` with a reason when it does not apply. Do not invent tests for wording-only or otherwise low-impact edits.

Present the completed spec with the remaining consequential assumptions in one concise summary. Obtain approval of that concrete plan unless the user has already authorized it or explicitly delegated the plan decisions. An explicit "go ahead" on the presented plan counts; do not require a second section-by-section recital. Incorporate corrections and re-present only material changes needing a decision.

Use a question tool when available and appropriate to its rules; otherwise ask in chat. Silence is never approval. If the user asks for autonomous execution, use reasonable decisions within that scope and continue.
