#!/usr/bin/env python3
"""Export the validated skills catalog as deterministic schema-v1 JSON."""
import argparse
import json
from pathlib import Path
import sys

from catalog_contract import load_catalog


CATALOG_SCHEMA_VERSION = 1


def export_catalog(repo):
    """Return the portable catalog projection for ``repo``."""
    skills = []
    for name, description, targets in load_catalog(repo):
        skills.append({
            "name": name,
            "description": description,
            "source": f"skills/{name}/SKILL.md",
            "targets": sorted(targets),
        })
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "skills": skills,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="skills repository to export (defaults to this checkout)",
    )
    args = parser.parse_args(argv)
    try:
        # Serialize completely before writing so validation or encoding errors
        # can never leave a partial JSON document on stdout.
        output = json.dumps(
            export_catalog(args.repo),
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        ) + "\n"
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print(f"Catalog export error: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
