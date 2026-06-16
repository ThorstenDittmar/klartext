"""Infrastructure tests: the F0.3 method path-classification + well-formedness gate.

The mechanical half of the F0 acceptance criterion (ADR-0013):

  * **half-(i) path classification** — method content lives only in the L3/L2 stems; the migrated
    legacy tree `docs/superpowers/improvement/**` must stay empty; a card must not be *half-split*
    (carry both an `Essence type:` self-definition AND an `L3 definition:` delegation pointer — OE's
    mechanical "mixed card" signal). Semantic bleed is SA's well-formedness *review*, not the gate.
  * **half-(ii) well-formedness** — every element card is type-conditionally well-formed per
    `docs/method/library/_card-template.md` (SA-ratified CI scope):
      - every standalone card: a clean `Essence type` enum token + an `External dependencies` field;
      - practice cards also: `Advances Alpha` + `Work Products` + `Activity / Activity Space`;
      - an L2 practice card is **delegate-XOR-standalone** (OE 2026-06-16): either an
        `L3 definition:` pointer (no own type/§3 needed) or the standalone fields inline.

Card-set boundary (DevOps mechanism, flagged for OE/SA at the gate): the card set is the typed/
delegating element cards under `library/{practices,patterns,resources}`, `enactment/practices`, plus
the named L3 element card `dependency-contract.md`. The `enactment/contracts/` files are
dependency-contract *instances* (prose-link references to the L3 element card), not element cards.

The pure `card_violations` logic is unit-gated against synthetic cards; a final test asserts the
real method tree on main passes both halves (the F0-acceptance assertion OE establishes on the PR).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import method_classification as mc  # noqa: E402

# --- half-(ii) well-formedness: standalone cards ------------------------------------------

_GOOD_L3_PRACTICE = """# Example — generic

> **Essence type:** Practice
> **Advances Alpha:** Way of Working  ·  **Work Products:** a report
> **Activity / Activity Space:** Test the System → do the thing
> **External dependencies (referenced Resources):** none
"""


def test_well_formed_l3_practice_has_no_violations() -> None:
    """Expects a standalone L3 practice card with type + external deps + §3 to be well-formed."""
    assert mc.card_violations("docs/method/library/practices/example.md", _GOOD_L3_PRACTICE) == []


def test_practice_missing_essence_type_and_delegation_is_malformed() -> None:
    """Expects a practice card with neither an Essence type nor an L3 pointer to fail."""
    text = (
        "# X\n\n> **Advances Alpha:** A · **Work Products:** w\n"
        "> **Activity / Activity Space:** s\n"
    )
    violations = mc.card_violations("docs/method/library/practices/x.md", text)
    assert violations
    assert any("Essence type" in v for v in violations)


def test_practice_missing_a_section3_field_is_malformed() -> None:
    """Expects a standalone practice card missing 'Work Products' to be flagged."""
    text = (
        "# X\n\n> **Essence type:** Practice\n"
        "> **Advances Alpha:** A\n"
        "> **Activity / Activity Space:** s\n"
        "> **External dependencies (referenced Resources):** none\n"
    )
    violations = mc.card_violations("docs/method/library/practices/x.md", text)
    assert any("Work Products" in v for v in violations)


def test_standalone_card_missing_external_dependencies_is_malformed() -> None:
    """Expects a typed card with no External dependencies field to fail (silence not allowed)."""
    text = "# Pat\n\n> **Essence type:** Pattern\n"
    violations = mc.card_violations("docs/method/library/patterns/pat.md", text)
    assert any("External dependencies" in v for v in violations)


def test_invalid_essence_type_token_is_malformed() -> None:
    """Expects an Essence type that is not a clean enum token to be flagged."""
    text = "# X\n\n> **Essence type:** Practice (ritual)\n> **External dependencies:** none\n"
    violations = mc.card_violations("docs/method/library/patterns/x.md", text)
    assert any("Essence type" in v for v in violations)


def test_activity_is_a_valid_essence_type() -> None:
    """Expects 'Activity' to be accepted (e2e-before-done / naht-check use it)."""
    text = "# A\n\n> **Essence type:** Activity\n> **External dependencies:** none\n"
    assert mc.card_violations("docs/method/library/patterns/a.md", text) == []


# --- half-(ii): L2 practice delegate-XOR-standalone ---------------------------------------


def test_delegating_l2_practice_is_well_formed() -> None:
    """Expects an L2 practice card delegating via an L3-definition pointer to need nothing else."""
    text = (
        "# X — klartext enactment\n\n> **Scope.** bindings only.\n"
        "> **L3 definition:** [`../../library/practices/x.md`](../../library/practices/x.md)\n"
        "> **Status:** living · **Owner:** OE\n"
    )
    assert mc.card_violations("docs/method/enactment/practices/x.md", text) == []


def test_standalone_l2_practice_needs_inline_fields() -> None:
    """Expects a wholly-L2 practice (no L3 pointer) to require the inline standalone + §3 fields."""
    text = "# X — klartext\n\n> **Scope.** wholly-L2.\n> **Status:** living\n"
    violations = mc.card_violations("docs/method/enactment/practices/x.md", text)
    assert violations  # neither delegates nor carries inline fields


def test_card_with_both_essence_type_and_l3_definition_is_mixed() -> None:
    """Expects the half-split guard: a card carrying BOTH Essence type and L3 definition fails."""
    text = (
        "# X\n\n> **Essence type:** Practice\n"
        "> **L3 definition:** [`../../library/practices/x.md`](../../library/practices/x.md)\n"
    )
    violations = mc.card_violations("docs/method/enactment/practices/x.md", text)
    assert any("mixed" in v.lower() or "both" in v.lower() for v in violations)


def test_non_practice_card_may_not_delegate() -> None:
    """Expects a non-practice card (pattern) using an L3-definition pointer to be flagged.

    Delegation is the L2-practice split mechanism; a pattern/resource/element card is its own
    definition and must stand alone.
    """
    text = "# Pat\n\n> **L3 definition:** [`x`](x)\n"
    violations = mc.card_violations("docs/method/library/patterns/pat.md", text)
    assert violations


# --- half-(i) path classification: legacy tree must stay empty ----------------------------


def test_legacy_improvement_tree_with_a_file_is_a_violation(tmp_path: Path) -> None:
    """Expects a file under docs/superpowers/improvement/ to be reported (must stay empty)."""
    legacy = tmp_path / "docs" / "superpowers" / "improvement" / "practices"
    legacy.mkdir(parents=True)
    (legacy / "leaked.md").write_text("method content in the old place")

    violations = mc.legacy_violations(tmp_path)

    assert any("improvement" in v for v in violations)


def test_empty_legacy_tree_has_no_violations(tmp_path: Path) -> None:
    """Expects an absent/empty legacy improvement tree to produce no violation."""
    assert mc.legacy_violations(tmp_path) == []


# --- parser + card-set + aggregation (regression guards) ----------------------------------


def test_essence_type_with_trailing_inline_fields_is_parsed_and_accepted() -> None:
    """Expects a type token followed by other ·-separated fields on the same line to parse cleanly.

    Cards often write `**Essence type:** Practice · **Advances Alpha:** …` on one line; the token
    extractor must yield 'Practice' (not the whole line) and the inline §3 fields must be detected.
    """
    text = (
        "# X\n\n> **Essence type:** Practice · **Advances Alpha:** A · **Work Products:** w\n"
        "> **Activity / Activity Space:** s\n"
        "> **External dependencies (referenced Resources):** none\n"
    )
    assert mc.card_violations("docs/method/library/practices/x.md", text) == []


def test_l3_card_carrying_both_type_and_l3_definition_is_mixed() -> None:
    """Expects the half-split guard to apply to L3 cards too (not only enactment cards)."""
    text = "# X\n\n> **Essence type:** Practice\n> **L3 definition:** [x](x)\n"
    violations = mc.card_violations("docs/method/library/practices/x.md", text)
    assert any("half-split" in v.lower() or "both" in v.lower() for v in violations)


def test_find_card_paths_selects_cards_and_excludes_readmes_templates_contracts(
    tmp_path: Path,
) -> None:
    """Expects find_card_paths to pick element cards, the named element card, and skip the rest.

    READMEs and `_`-prefixed templates inside a card dir are excluded; the enactment/contracts/
    instances are not element cards; the named dependency-contract.md is included.
    """
    (tmp_path / "docs/method/library/practices").mkdir(parents=True)
    (tmp_path / "docs/method/library/practices/tdd.md").write_text("c")
    (tmp_path / "docs/method/library/practices/README.md").write_text("c")
    (tmp_path / "docs/method/library/practices/_template.md").write_text("c")
    (tmp_path / "docs/method/library/dependency-contract.md").write_text("c")
    (tmp_path / "docs/method/enactment/contracts").mkdir(parents=True)
    (tmp_path / "docs/method/enactment/contracts/memory-substrate.md").write_text("c")

    names = {p.name for p in mc.find_card_paths(tmp_path)}

    assert "tdd.md" in names
    assert "dependency-contract.md" in names
    assert "README.md" not in names
    assert "_template.md" not in names
    assert "memory-substrate.md" not in names  # contracts are instances, not element cards


def test_check_tree_reports_both_legacy_and_card_violations(tmp_path: Path) -> None:
    """Expects check_tree to aggregate a leaked legacy file AND a malformed card in one run."""
    (tmp_path / "docs/superpowers/improvement").mkdir(parents=True)
    (tmp_path / "docs/superpowers/improvement/leak.md").write_text("method content")
    (tmp_path / "docs/method/library/practices").mkdir(parents=True)
    (tmp_path / "docs/method/library/practices/bad.md").write_text("# bad\n\n> no fields\n")

    violations = mc.check_tree(tmp_path)

    assert any("improvement" in v for v in violations)
    assert any("bad.md" in v for v in violations)


# --- the F0-acceptance assertion: the real method tree passes both halves -----------------


def test_real_method_tree_passes_the_gate() -> None:
    """Expects the live method tree on main to be fully classified + well-formed (F0-acceptance).

    The encoded gate OE establishes on the PR: every card under docs/method/ is well-formed and the
    legacy improvement tree is empty. On failure, the offending card/path is named in the message.
    """
    violations = mc.check_tree(_REPO_ROOT)
    assert violations == [], "method tree not clean:\n" + "\n".join(violations)
