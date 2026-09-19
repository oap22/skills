"""Shared validation contract for the canonical skills catalog.

This module is intentionally dependency-free and contains no OAS concepts.
Installers, renderers, and exporters must consume this validator instead of
growing their own interpretations of ``manifest.json`` or skill frontmatter.
"""
import json
from pathlib import Path
import re


MANIFEST_SCHEMA_VERSION = 1
TARGET_LAYOUTS = {
    "claude": (".claude", "skills"),
    "cursor": (".cursor", "skills"),
    "codex": (".codex", "skills"),
    "gemini": (".gemini", "skills"),
    "vault": ("Owen's Awesome Vault", ".claude/skills"),
}
TARGET_NAMES = frozenset(TARGET_LAYOUTS)
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _has_surrogate(value):
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _scalar(value):
    """Accept this repository's deliberately small YAML string subset."""
    if value.startswith('"'):
        result = json.loads(value)
    elif value.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", value):
            raise ValueError("invalid single-quoted string")
        result = value[1:-1].replace("''", "'")
    else:
        if (not value or value[0] in "[]{}&*!|>@`%#,-?:" or
                ": " in value or " #" in value or
                value.lower() in {"true", "false", "null", "~", "yes", "no", "on", "off"} or
                re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value)):
            raise ValueError("quote this scalar with JSON double quotes")
        result = value
    if (not isinstance(result, str) or not result.strip() or
            any(separator in result for separator in ("\r", "\n", "\u2028", "\u2029"))):
        raise ValueError("expected a nonempty one-line string")
    if _has_surrogate(result):
        raise ValueError("string contains a lone Unicode surrogate")
    return result


def _frontmatter(name, source):
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"{name}: cannot read SKILL.md: {exc}") from exc
    block = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not block:
        raise ValueError(f"{name}: missing frontmatter delimiters")
    fields = {}
    for line in block[1].splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep or key not in {"name", "description"}:
            raise ValueError(f"{name}: unsupported frontmatter field/structure: {key!r}")
        if key in fields:
            raise ValueError(f"{name}: duplicate {key}")
        try:
            fields[key] = _scalar(value.strip())
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{name}: invalid {key}: {exc}") from exc
    if fields.get("name") != name:
        raise ValueError(f"{name}: frontmatter name must match directory")
    description = fields.get("description")
    if not description:
        raise ValueError(f"{name}: missing valid description")
    if len(description) > 1024:
        raise ValueError(f"{name}: description exceeds 1024 characters")
    if not text[block.end():].strip():
        raise ValueError(f"{name}: empty skill body")
    return description


def _validate_source(repo, name):
    skills_root = repo / "skills"
    folder = skills_root / name
    source = folder / "SKILL.md"
    if skills_root.is_symlink() or not skills_root.is_dir():
        raise ValueError("skills: expected a local regular directory")
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError(f"{name}: expected a local regular skill directory")
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"{name}: expected a regular SKILL.md")
    try:
        repo_resolved = repo.resolve(strict=True)
        source_resolved = source.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"{name}: cannot resolve skill source: {exc}") from exc
    if source_resolved != repo_resolved and repo_resolved not in source_resolved.parents:
        raise ValueError(f"{name}: skill source resolves outside the repository")
    return source


def load_catalog(repo):
    """Load and validate manifest v1 plus all referenced skill metadata.

    A missing ``schema_version`` is accepted as legacy manifest v1 input.
    All consumers use the canonical target registry defined in this module.
    """
    repo = Path(repo)
    try:
        manifest = json.loads(
            (repo / "manifest.json").read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest.json: {exc}") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("skills"), dict):
        raise ValueError("manifest.json: manifest must contain a skills object")
    schema_version = manifest.get("schema_version", MANIFEST_SCHEMA_VERSION)
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise ValueError("manifest.json: schema_version must be an integer")
    if schema_version != MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            f"manifest.json: unsupported schema_version {schema_version}; "
            f"expected {MANIFEST_SCHEMA_VERSION}"
        )

    rows = []
    for name, targets in sorted(manifest["skills"].items()):
        if (not isinstance(name, str) or _has_surrogate(name) or
                len(name) > 64 or not NAME.fullmatch(name)):
            raise ValueError(f"invalid skill name: {name!r}")
        if not isinstance(targets, list) or not targets:
            raise ValueError(f"{name}: targets must be a nonempty list")
        seen = set()
        for target in targets:
            if (not isinstance(target, str) or _has_surrogate(target) or
                    target not in TARGET_NAMES):
                raise ValueError(f"{name}: unknown harness {target!r}")
            if target in seen:
                raise ValueError(f"{name}: duplicate harness {target}")
            seen.add(target)
        source = _validate_source(repo, name)
        rows.append((name, _frontmatter(name, source), targets))
    return rows
