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
    """Identifies which scenes should have claims extracted via the API."""

    scene_index: int


SEED_CLAIMS: list[SeedClaims] = [
    SeedClaims(scene_index=0),
    SeedClaims(scene_index=1),
    SeedClaims(scene_index=2),
]


# ---------------------------------------------------------------------------
# Causal model seed data
# ---------------------------------------------------------------------------


@dataclass
class SeedAxiom:
    """A single axiom for the causal model seed data."""

    label: str
    description: str


@dataclass
class SeedCausalModel:
    """Pre-defined causal model with axioms for the Klartext narrative."""

    title: str
    axioms: list[SeedAxiom]


SEED_CAUSAL_MODEL = SeedCausalModel(
    title="Wirkmodell: Zinserhöhungen und gesellschaftliche Folgen",
    axioms=[
        SeedAxiom(
            label="Zinserhöhungen senken die Inflation",
            description=(
                "Höhere Leitzinsen verteuern Kredite und dämpfen damit Konsum und "
                "Investitionen, was den Preisauftrieb reduziert."
            ),
        ),
        SeedAxiom(
            label="Zentralbankentscheidungen beeinflussen das institutionelle Vertrauen",
            description=(
                "Wie die EZB Entscheidungen kommuniziert und begründet, wirkt sich "
                "direkt darauf aus, wie viel Vertrauen die Bevölkerung in die Institution hat."
            ),
        ),
        SeedAxiom(
            label="Verlässliche Geldpolitik stabilisiert Erwartungen",
            description=(
                "Wenn Zentralbanken konsistent und transparent handeln, können "
                "Unternehmen und Haushalte besser planen — das reduziert Unsicherheit."
            ),
        ),
        SeedAxiom(
            label="Zinserhöhungen erhöhen die Kreditkosten für Haushalte",
            description=(
                "Steigende Leitzinsen schlagen sich in höheren Hypotheken- und "
                "Konsumkreditzinsen nieder, was die finanzielle Belastung vieler "
                "Haushalte direkt erhöht."
            ),
        ),
    ],
)


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
