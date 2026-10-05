---
name: python-docstrings
description: "Write Google-style docstrings (summary, Args, Returns/Yields, Raises) for Python functions, methods, and classes in any project. Use for \"add a docstring\", \"document this function\", or a request for docstrings in \"the standard format\" with no style named. In professor mode on graded code, explain or check the format instead of writing it."
---

# Python Docstrings

Use Google style when writing a Python docstring and no other convention applies. A one-liner meets PEP 257's minimum, but rubric and review checks usually expect parameters and the return value spelled out.

## Steps

1. Write a short, imperative one-line summary as the first line (e.g., "Generate a list of random birthdays.", not "This function generates..."). If the file's existing docstrings use the descriptive form ("Generates..."), match it.
2. If the function takes parameters, add a blank line, then `Args:`, listing each parameter as `name: description.` Add a type only for an unannotated parameter (`name (int): ...`). Indent wrapped lines 4 more spaces. Never list `self` or `cls`.
3. If the function returns a non-`None` value, add a blank line, then `Returns:` describing what's returned; give the type or shape only when the signature does not annotate it. A generator gets `Yields:` instead. Exceptions raised on purpose for callers to handle go under `Raises:` as `ExcType: condition.`
4. Omit `Args:` for no-argument functions and `Returns:` for functions that return `None` — don't include empty or vacuous sections.
5. For a class, the summary says what one instance represents, with public attributes under `Attributes:`; constructor `Args:` go in `__init__`'s docstring unless the codebase puts them on the class.
6. Use triple double-quotes (`"""..."""`) as the first statement in the body, before any code.

```python
def random_birthdays(n):
    """Generate a list of random birthdays.

    Args:
        n: Number of birthdays to generate.

    Returns:
        A list of n day-of-year integers in [1, 365].
    """
```

If ruff is available, check with `ruff check --preview --select D,DOC` and the project's convention (or `--config 'lint.pydocstyle.convention="google"'`). It checks section format and Yields/Returns/Raises against the code; it does not prove a `Returns:` section is present or catch `self` under `Args:`.

## Rules

- Don't invent parameter descriptions the user hasn't explained — infer conservatively from the name and function body, and flag anything genuinely ambiguous instead of guessing.
- If the project already has a convention, match it instead of forcing Google style: a `convention` under `[tool.ruff.lint.pydocstyle]` or `[tool.pydocstyle]` in `pyproject.toml` or `setup.cfg`, or NumPy/reST docstrings in the file or its sibling modules.
- This is a formatting convention, not permission to add or change docstrings on code the user hasn't asked you to touch — apply it when writing/editing a docstring that's already in scope for the task.
- In professor mode, a docstring on graded assignment code is part of the student's work: explain this format or check the one they wrote, but do not write it into their file.

## Gotchas

None recorded yet. Add one here when a run fails a new way.
