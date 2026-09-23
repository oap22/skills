---
name: python-docstrings
description: "Write Google-style docstrings (one-line summary, Args, Returns) for Python functions in any project. Use for \"add a docstring\", \"document this function\", or a request for docstrings in \"the standard format\" with no style named."
---

# Python Docstrings

Default to Google-style docstrings for any Python function worth documenting — not just coursework. A bare one-line docstring satisfies PEP 257's minimum, but most "properly formatted docstring" rubric or review checks expect parameters and return value spelled out, so treat the one-liner as the floor, not the target, once a function takes arguments or returns something non-trivial.

## Steps

1. Write a short, imperative one-line summary as the first line (e.g., "Generate a list of random birthdays.", not "This function generates...").
2. If the function takes parameters, add a blank line, then `Args:`, listing each parameter as `name: description.` — one line per parameter.
3. If the function returns a non-`None` value, add a blank line, then `Returns:` describing what's returned and its shape/type.
4. Omit `Args:` for no-argument functions and `Returns:` for functions that return `None` — don't include empty or vacuous sections.
5. Use triple double-quotes (`"""..."""`) as the first statement in the function body, before any code.

## Rules

- Don't invent parameter descriptions the user hasn't explained — infer conservatively from the name and function body, and flag anything genuinely ambiguous instead of guessing.
- If the surrounding codebase already has an established docstring convention (NumPy-style, reST, or existing docstrings elsewhere in the file using a different format), match that instead of forcing Google-style — consistency within a codebase wins over this default.
- This is a formatting convention, not permission to add or change docstrings on code the user hasn't asked you to touch — apply it when writing/editing a docstring that's already in scope for the task.
