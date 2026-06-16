#!/usr/bin/env python3
"""CI path-scope — decide which App check groups a change needs to run.

#1a coarse CI scoping (methode/app separation): a change confined to the collaboration
method / environment (docs/**, agents/**, .claude/**) does not need the App checks. The
App checks are *required* status checks, so the workflow job must always run and report
success — only the expensive steps are guarded by this decision. A wrongly-skipped
required check is invisible breakage, so the rule is deliberately conservative:

  * api / frontend each run UNLESS the change provably does not touch them.
  * Any shared / unknown / repo-root path (e.g. .github/**, pyproject.toml, README.md)
    forces BOTH groups to run.
  * No changed paths at all (push event, diff failure) forces BOTH groups to run.

Used by the App workflows (lint/test/integration/qa), which collect the changed paths and
gate their expensive steps on this module's output. The decision lives in this one
importable module so it is testable without a live PR.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

# Paths that are method / environment only — never trigger an App check on their own.
METHOD_PREFIXES: tuple[str, ...] = ("docs/", "agents/", ".claude/")


@dataclass(frozen=True)
class Scope:
    """Which App check groups a change needs: True = run, False = safe to skip."""

    api: bool
    frontend: bool


def decide(changed_paths: list[str]) -> Scope:
    """Decides which App check groups must run for the given changed paths.

    Conservative by contract: returns Scope(True, True) for empty input or any shared/
    unknown path; only skips a group when every changed path is provably unrelated to it.
    """
    paths = [p.strip() for p in changed_paths if p.strip()]
    if not paths:
        return Scope(api=True, frontend=True)

    api = False
    frontend = False
    for path in paths:
        if path.startswith("api/"):
            api = True
        elif path.startswith("frontend/"):
            frontend = True
        elif path.startswith(METHOD_PREFIXES):
            continue  # method/environment only — does not pull in any App check
        else:
            # Shared / unknown / repo-root path: cannot prove irrelevance -> run everything.
            return Scope(api=True, frontend=True)
    return Scope(api=api, frontend=frontend)


def _parse_list(raw: str) -> list[str]:
    """Parses a list from a JSON array or a newline/comma-separated string. Empty -> []."""
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        return [str(x).strip() for x in json.loads(raw) if str(x).strip()]
    parts = raw.replace(",", "\n").splitlines()
    return [p.strip() for p in parts if p.strip()]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: prints GITHUB_OUTPUT-style key=value lines, always returns 0.

    --changed-paths accepts a newline- or comma-separated string (or a JSON array), so the
    workflow can pass `gh pr diff --name-only` output directly and append stdout to
    $GITHUB_OUTPUT. ci_scope reports scope; it never fails the job (it is not a gate).
    """
    parser = argparse.ArgumentParser(description="CI path-scope (api/frontend).")
    parser.add_argument(
        "--changed-paths",
        default="",
        help="changed file paths (newlines, commas, or JSON array)",
    )
    args = parser.parse_args(argv)

    scope = decide(_parse_list(args.changed_paths))
    print(f"api={str(scope.api).lower()}")
    print(f"frontend={str(scope.frontend).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
