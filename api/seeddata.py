"""Seed data for klartext.jetzt.

Defines a consistent, realistic dataset based on the Klartext story.
Used by `klartext testdata` to populate a running system for manual
testing and development.

This module is independent of the test infrastructure — it uses the
real repositories and can be called from the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from api.models.claim import Claim, ClaimType
from api.models.narrative import Narrative, Scene


# ---------------------------------------------------------------------------
# Narrative seed data
# ---------------------------------------------------------------------------

FIXTURE_PATH = (
    Path(__file__).parent
    / "tests"
    / "fixtures"
    / "klartext-eine-geschichte-ueber-eine-geschichte"
    / "narrative.md"
)


@dataclass
class SeedClaims:
    """Pre-defined claims for each scene of the Klartext narrative."""

    scene_index: int
    claims: list[Claim]


SEED_CLAIMS: list[SeedClaims] = [
    SeedClaims(
        scene_index=0,
        claims=[
            Claim.create(
                text="Öffentliche Debatten sind zunehmend von Lärm geprägt, nicht von Argumenten.",
                typ=ClaimType.EMPIRICAL,
                confidence=0.8,
            ),
            Claim.create(
                text=(
                    "Die Fähigkeit, die Perspektive anderer nachzuvollziehen, "
                    "nimmt in polarisierten Gesellschaften ab."
                ),
                typ=ClaimType.CAUSAL,
                confidence=0.75,
            ),
        ],
    ),
    SeedClaims(
        scene_index=1,
        claims=[
            Claim.create(
                text="Interdisziplinäre Hintergründe fördern die Qualität von Debatten.",
                typ=ClaimType.NORMATIVE,
                confidence=0.7,
            ),
        ],
    ),
    SeedClaims(
        scene_index=2,
        claims=[
            Claim.create(
                text=(
                    "Transparente Wirkmodelle ermöglichen es, Meinungsverschiedenheiten "
                    "auf ihre Grundannahmen zurückzuführen."
                ),
                typ=ClaimType.CAUSAL,
                confidence=0.85,
            ),
            Claim.create(
                text="Kausal konsistente Narrative sind seltener als normativ aufgeladene.",
                typ=ClaimType.EMPIRICAL,
                confidence=0.65,
            ),
        ],
    ),
]


def build_simple_narrative() -> Narrative:
    """Builds a small, self-contained narrative for quick smoke tests.

    Does not require the fixture file — useful when the full story is not needed.
    """
    narrative = Narrative.create(title="Klartext – Kurzversion (Seed)")
    narrative.add_scene(
        Scene.create(
            title="Szene 1 – Der Abend",
            text=(
                "Der Abend, an dem sie aufgehört hatten, miteinander zu reden, "
                "war kein besonderer Abend gewesen. Mara hatte ihren Laptop zugeklappt "
                "und gesagt: Ich kann nicht mehr."
            ),
            position=1,
        )
    )
    narrative.add_scene(
        Scene.create(
            title="Szene 2 – Die Begegnung",
            text=(
                "Tarek hatte sie beide kennengelernt über einen dieser Abende, "
                "die niemand wirklich geplant hatte. Sie hatten sich über irgendetwas "
                "gestritten — und danach weitergetrunken, weil der Streit gut gewesen war."
            ),
            position=2,
        )
    )
    narrative.add_scene(
        Scene.create(
            title="Szene 3 – Das Modell",
            text=(
                "Was wäre, wenn man nicht über Meinungen streiten würde, "
                "sondern über Wirkmodelle? Über die Annahmen, die hinter den Meinungen stecken?"
            ),
            position=3,
        )
    )
    return narrative
