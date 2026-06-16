#!/usr/bin/env python3
"""Method path-classification + well-formedness gate (F0.3, ADR-0013).

The mechanical half of the F0 acceptance criterion. Two checks over the working tree:

  * **half-(i) path classification** — the migrated legacy tree `docs/superpowers/improvement/**`
    must stay empty (its content moved to `docs/method/{library,enactment}/` in F0.1/F0.2), and no
    card may be *half-split* (carry both an `Essence type:` self-definition AND an `L3 definition:`
    delegation pointer — OE's mechanical "mixed card" signal). Semantic bleed (klartext evidence in an
    L3 card, etc.) is **not** mechanically checkable and stays SA's well-formedness review.
  * **half-(ii) well-formedness** — every Essence element card is type-conditionally well-formed per
    `docs/method/library/_card-template.md` (SA-ratified CI scope, PR #137/#142/#150):
      - every standalone card: a clean `Essence type` enum token + an `External dependencies` field
        (`none` is allowed; silence is not);
      - practice cards additionally: `Advances Alpha` + `Work Products` + `Activity / Activity Space`;
      - an L2 practice card is **delegate-XOR-standalone**: it either delegates via an `L3 definition:`
        pointer (then it needs neither its own type nor §3 — they live on the L3 sibling) or carries the
        standalone fields inline. Carrying both is the half-split contradiction above.

Card set (DevOps mechanism): the typed/delegating element cards under `library/{practices,patterns,
resources}`, `enactment/practices`, and the named L3 element card `dependency-contract.md`. The
`enactment/contracts/` files are dependency-contract *instances* (prose-link references to the L3 element
card), not element cards, and are out of the card check.

Used by .github/workflows/method-classification.yml, which runs this module over the checked-out tree
and forwards the exit code (0 = clean, 1 = violations). The logic lives here (not inline YAML) following
the scripts/ + api/tests/infrastructure/ pattern (classify_gate, converge, session_health).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Clean Essence-type enum tokens (clarifiers must be kept OUT of the value — _card-template.md).
VALID_ESSENCE_TYPES: frozenset[str] = frozenset(
    {"Practice", "Pattern", "Work Product", "Resource", "Method", "Alpha", "Activity"}
)

# Directories whose every `.md` is an element card (relative to the repo root).
CARD_DIRS: tuple[str, ...] = (
    "docs/method/library/practices",
    "docs/method/library/patterns",
    "docs/method/library/resources",
    "docs/method/enactment/practices",
)
# Named element cards that live at a stem root rather than in a card directory.
NAMED_CARD_FILES: tuple[str, ...] = ("docs/method/library/dependency-contract.md",)

# Legacy method trees that F0/F3 emptied and that must stay empty. `improvement/` migrated in F0.1/F0.2;
# `skills/` migrated in F3 #3b (executables → docs/method/enactment/skills/; generic defs stay in L3 cards).
LEGACY_EMPTY_DIRS: tuple[str, ...] = (
    "docs/superpowers/improvement",
    "docs/superpowers/skills",
)

_TYPE_MARKER = "**Essence type:**"
_L3DEF_MARKER = "**L3 definition:**"
_EXTERNAL_DEPS_MARKER = "**External dependencies"
_SECTION3_LABELS: tuple[str, ...] = (
    "**Advances Alpha:**",
    "**Work Products:**",
    "**Activity / Activity Space:**",
)


def _essence_type_token(text: str) -> str | None:
    """Returns the Essence-type value as written, or None if the field is absent.

    Takes the text after the marker up to the line end, then cuts at the first field separator
    (`·`/`|`) or the next bold field (`**`) — so a clean token survives but a trailing clarifier
    (e.g. `Practice (ritual)`) is kept attached and rejected by the enum check.
    """
    match = re.search(r"\*\*Essence type:\*\*\s*([^\n]*)", text)
    if match is None:
        return None
    raw = match.group(1)
    return re.split(r"\s*[·|]\s*|\s*\*\*", raw, maxsplit=1)[0].strip()


def card_violations(rel_path: str, text: str) -> list[str]:
    """Returns the well-formedness violations for one card's text (empty list = well-formed).

    Implements the type-conditional, delegate-XOR-standalone rules. `rel_path` decides whether the card
    is a practice card (path contains `/practices/`); `text` carries the field markers.
    """
    violations: list[str] = []
    has_type = _TYPE_MARKER in text
    has_l3def = _L3DEF_MARKER in text
    is_practice = "/practices/" in rel_path

    # half-(i) half-split guard: a card may self-define (Essence type) or delegate (L3 definition),
    # never both — that is a card caught mid-split.
    if has_type and has_l3def:
        return [
            f"{rel_path}: half-split — carries both 'Essence type' and 'L3 definition'"
        ]

    # Delegation: only a practice card may delegate to an L3 sibling; it then needs nothing else.
    if has_l3def:
        if not is_practice:
            violations.append(
                f"{rel_path}: non-practice card delegates via 'L3 definition' — only practice cards may"
            )
        return violations

    # Standalone path (no delegation): an Essence type is mandatory.
    if not has_type:
        violations.append(
            f"{rel_path}: missing 'Essence type' and no 'L3 definition' delegation pointer"
        )
        return violations

    token = _essence_type_token(text)
    if token not in VALID_ESSENCE_TYPES:
        violations.append(
            f"{rel_path}: 'Essence type' is not a clean enum token: {token!r}"
        )

    if _EXTERNAL_DEPS_MARKER not in text:
        violations.append(
            f"{rel_path}: missing 'External dependencies' (write 'none' if empty — silence not allowed)"
        )

    if is_practice:
        for label in _SECTION3_LABELS:
            if label not in text:
                violations.append(f"{rel_path}: practice card missing {label}")

    return violations


def find_card_paths(root: Path) -> list[Path]:
    """Returns every element-card file under the method stems (excludes contracts instances, READMEs)."""
    cards: list[Path] = []
    for card_dir in CARD_DIRS:
        for path in sorted((root / card_dir).glob("*.md")):
            if path.name == "README.md" or path.name.startswith("_"):
                continue
            cards.append(path)
    for named in NAMED_CARD_FILES:
        path = root / named
        if path.exists():
            cards.append(path)
    return cards


def legacy_violations(root: Path) -> list[str]:
    """Returns a violation per file found under a legacy-empty tree (path classification, half-i)."""
    violations: list[str] = []
    for legacy in LEGACY_EMPTY_DIRS:
        base = root / legacy
        if not base.exists():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            violations.append(
                f"{path.relative_to(root).as_posix()}: method content in the emptied legacy tree "
                f"'{legacy}/' — it must move to docs/method/{{library,enactment}}/"
            )
    return violations


def check_tree(root: Path) -> list[str]:
    """Returns all path-classification + well-formedness violations for the method tree under `root`."""
    violations = legacy_violations(root)
    for path in find_card_paths(root):
        violations.extend(
            card_violations(path.relative_to(root).as_posix(), path.read_text())
        )
    return violations


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: scans the repo's method tree, prints violations, returns 0 (clean) or 1."""
    root = Path(__file__).resolve().parents[1]
    violations = check_tree(root)
    if not violations:
        print(
            "✓  method tree classified + well-formed (F0 acceptance: path + well-formedness)."
        )
        return 0
    print("✗  method classification gate failed:")
    for violation in violations:
        print(f"   - {violation}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
