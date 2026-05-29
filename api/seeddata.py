"""Seed data for klartext.jetzt.

Defines a consistent, realistic dataset based on the Klartext story.
Used by `klartext testdata` to populate a running system for manual
testing and development.

This module is independent of the test infrastructure — it uses the
real repositories and can be called from the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from api.models.narrative import Narrative, Scene


# ---------------------------------------------------------------------------
# Narrative seed data
# ---------------------------------------------------------------------------

FIXTURE_PATH = (
    Path(__file__).parent
    / "tests"
    / "fixtures"
    / "klartext-eine-geschichte-ueber-eine-geschichte"
    / "narrative.docx"
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
# Actor seed data
# ---------------------------------------------------------------------------


@dataclass
class SeedActor:
    """A single actor definition for the narrative seed data."""

    name: str
    typ: str  # ActorType value (German string: 'figur', 'organisation', etc.)
    description: Optional[str] = field(default=None)


SEED_ACTORS: list[SeedActor] = [
    SeedActor(
        name="Mara",
        typ="figur",
        description="Autorin und Mitgründerin von klartext.jetzt.",
    ),
    SeedActor(
        name="Tarek",
        typ="figur",
        description="Entwickler und Mitgründer von klartext.jetzt.",
    ),
    SeedActor(
        name="klartext.jetzt",
        typ="organisation",
        description="Die Plattform für epistemische Publikationen.",
    ),
    SeedActor(
        name="Öffentlichkeit",
        typ="abstrakte_entitaet",
        description="Die abstrakte Gemeinschaft der Debattenteilnehmer.",
    ),
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
    title="Wirkmodell: Warum öffentliche Debatten scheitern",
    axioms=[
        SeedAxiom(
            label="Unsichtbare Annahmen verhindern Verständigung",
            description=(
                "Wenn Debattenteilnehmer ihre Grundannahmen nicht offenlegen, reden sie "
                "aneinander vorbei — nicht weil ihre Positionen unvereinbar sind, sondern "
                "weil niemand weiß, wo der andere wirklich steht."
            ),
        ),
        SeedAxiom(
            label="Explizite Prämissen machen Kritik möglich",
            description=(
                "Wer seine kausalen Annahmen benennt, ermöglicht es anderen, sachlich zu "
                "widersprechen. Ohne sichtbare Prämissen bleibt nur der Austausch von "
                "Behauptungen — nicht von Argumenten."
            ),
        ),
        SeedAxiom(
            label="Inklusion aller Stimmen schafft Legitimität",
            description=(
                "Eine Plattform, die auch unbequeme Positionen zulässt, gewinnt "
                "gesellschaftliche Glaubwürdigkeit. Wer nur unter Gleichgesinnten debattiert, "
                "verändert nichts."
            ),
        ),
        SeedAxiom(
            label="Regelbrüche werden durch Transparenz sichtbar",
            description=(
                "Wer in einem transparenten System strategisch lügt oder Prämissen "
                "verschleiert, macht das für alle sichtbar. Transparenz ist deshalb kein "
                "Risiko — sondern der wirksamste Schutz gegen Missbrauch."
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
