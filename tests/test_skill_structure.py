"""Authoring-structure checks over the real catalog (not enforced by the installer)."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
FENCE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.S | re.M)

# Shell gotchas that live once in the agent-system contract (prompts/core.md), not per skill.
SHARED_SHELL_GOTCHAS = (
    re.compile(r"`ls` is aliased", re.I),
    re.compile(r"/bin/ls"),
    re.compile(r"zsh (can )?aborts? on (non-matching|unmatched) glob", re.I),
)


def headings(text, level="## "):
    """Level-2 headings outside fenced code blocks."""
    return [line.strip() for line in FENCE.sub("", text).splitlines() if line.startswith(level)]


class HeadingParserTests(unittest.TestCase):
    def test_fenced_template_headings_are_ignored(self):
        text = "# T\n\n```markdown\n## Gotchas\n```\n\n## Steps\n"
        self.assertEqual(headings(text), ["## Steps"])

    def test_real_heading_counts(self):
        self.assertEqual(headings("## Gotchas\n\n- one\n"), ["## Gotchas"])


class SkillStructureTests(unittest.TestCase):
    def test_catalog_is_not_empty(self):
        self.assertGreater(len(SKILLS), 0)

    def test_every_skill_has_exactly_one_gotchas_section(self):
        for source in SKILLS:
            with self.subTest(skill=source.parent.name):
                found = headings(source.read_text(encoding="utf-8")).count("## Gotchas")
                self.assertEqual(found, 1, "add one `## Gotchas` section (README, Authoring rules)")

    def test_gotchas_section_is_not_empty(self):
        for source in SKILLS:
            with self.subTest(skill=source.parent.name):
                body = FENCE.sub("", source.read_text(encoding="utf-8")).split("\n## Gotchas\n", 1)[1]
                section = body.split("\n## ", 1)[0]
                self.assertTrue(section.strip(), "write a lesson or the 'None recorded yet' line")

    def test_shared_shell_gotchas_are_not_duplicated_in_skills(self):
        for source in sorted((ROOT / "skills").rglob("*.md")):
            text = source.read_text(encoding="utf-8")
            for pattern in SHARED_SHELL_GOTCHAS:
                with self.subTest(file=str(source.relative_to(ROOT)), pattern=pattern.pattern):
                    self.assertIsNone(pattern.search(text), "this gotcha lives in the agent-system prompts/core.md")


if __name__ == "__main__":
    unittest.main()
