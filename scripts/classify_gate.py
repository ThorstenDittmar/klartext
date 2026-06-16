#!/usr/bin/env python3
"""Classification gate — require a `rolling` | `breaking` label on Way-of-Working PRs.

A PR that touches a Way-of-Working (WoW) surface — method docs, agent Hoheitswissen, or
infrastructure config — must carry exactly one classification label that answers ADR-0012's
two-mode-consistency question explicitly:

  * rolling  — additive / backward-compatible; worktrees adopt it lazily via `klartext converge`.
  * breaking — changes the meaning of an existing rule/hook/path/contract; needs coordinated rollout.

The gate is default-free: it never infers the classification. PRs that touch no WoW surface
pass unconditionally, so ordinary code/test PRs are unaffected.

The trigger-path list is OE's literal list plus agents/**/claude.md and docs/method/** (the
migrated method library/enactment surface — added in F0.3 to close the gap where method changes
escaped the gate; see ADR-0013). Further broadening (e.g. .github/workflows/**) is a one-line
change here — see the design spec docs/superpowers/specs/2026-06-15-classification-gate-design.md.

Used by .github/workflows/classify-gate.yml, which collects the changed paths and the PR's
labels and forwards this module's exit code (0 = pass, 1 = fail).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

# Way-of-Working trigger patterns. A PR touching any matching path is "in scope" for the gate.
#   "<dir>/**"        -> any path under <dir>
#   "<head>**<tail>"  -> any path that starts with <head> and ends with <tail>
#   "<exact>"         -> that exact path
TRIGGER_PATTERNS: list[str] = [
    "CLAUDE.md",
    "docs/method/**",
    "agents/**/claude.md",
    ".claude/settings.json",
    "scripts/**",
    "api/cli.py",
]

VALID_LABELS: frozenset[str] = frozenset({"rolling", "breaking"})


@dataclass(frozen=True)
class GateResult:
    """Outcome of the classification gate: whether it passed and a human-readable message."""

    passed: bool
    message: str


def is_trigger_path(path: str) -> bool:
    """Returns True if a changed path is a Way-of-Working surface (matches a trigger pattern)."""
    for pattern in TRIGGER_PATTERNS:
        if pattern.endswith("/**"):
            prefix = pattern[:-2]  # keep the trailing slash, e.g. "scripts/"
            if path.startswith(prefix):
                return True
        elif "**" in pattern:
            head, tail = pattern.split("**", 1)
            if path.startswith(head) and path.endswith(tail):
                return True
        elif path == pattern:
            return True
    return False


def evaluate(changed_paths: list[str], labels: set[str]) -> GateResult:
    """Decides whether the classification gate passes.

    PASS if no changed path is a Way-of-Working surface (gate not applicable), or if a WoW
    surface is touched and exactly one of {rolling, breaking} is present. FAIL if a WoW
    surface is touched and neither or both labels are present. Never infers the label.
    """
    triggered = [p for p in changed_paths if is_trigger_path(p)]
    if not triggered:
        return GateResult(
            True,
            "No Way-of-Working surface touched — classification gate not applicable.",
        )

    present = VALID_LABELS & set(labels)
    touched = ", ".join(triggered)
    if len(present) == 1:
        label = next(iter(present))
        return GateResult(
            True, f"Classified '{label}'. Way-of-Working surfaces touched: {touched}."
        )
    if not present:
        return GateResult(
            False,
            "This PR touches Way-of-Working surfaces but carries no classification label. "
            "Add exactly one of 'rolling' or 'breaking' (uncertainty -> breaking; see ADR-0012). "
            f"Touched: {touched}.",
        )
    return GateResult(
        False,
        "This PR carries both 'rolling' and 'breaking' — exactly one is required. "
        f"Touched: {touched}.",
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: reads changed paths and labels, prints the verdict, returns 0/1.

    --changed-paths and --labels each accept a newline- or comma-separated string (or a JSON
    array), so the workflow can pass `git diff --name-only` output and the PR labels directly.
    """
    parser = argparse.ArgumentParser(
        description="Classification gate (rolling|breaking)."
    )
    parser.add_argument(
        "--changed-paths",
        default="",
        help="changed file paths (newlines, commas, or JSON array)",
    )
    parser.add_argument(
        "--labels", default="", help="PR label names (newlines, commas, or JSON array)"
    )
    args = parser.parse_args(argv)

    changed_paths = _parse_list(args.changed_paths)
    labels = set(_parse_list(args.labels))

    result = evaluate(changed_paths, labels)
    print(result.message)
    return 0 if result.passed else 1


def _parse_list(raw: str) -> list[str]:
    """Parses a list from a JSON array or a newline/comma-separated string. Empty -> []."""
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        return [str(x).strip() for x in json.loads(raw) if str(x).strip()]
    parts = raw.replace(",", "\n").splitlines()
    return [p.strip() for p in parts if p.strip()]


if __name__ == "__main__":
    sys.exit(main())
