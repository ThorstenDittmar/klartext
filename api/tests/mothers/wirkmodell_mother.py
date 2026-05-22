"""WirkmodellMother and AxiomMother — build Wirkmodell test objects."""

from __future__ import annotations

from api.models.wirkmodell import Axiom, Wirkmodell


class AxiomMother:
    """Factory for Axiom test objects."""

    @staticmethod
    def zins() -> Axiom:
        """Axiom about interest rates dampening investment — canonical example from the spec."""
        return Axiom.create(
            label="A-01",
            beschreibung="Drastische Zinserhöhungen dämpfen kurzfristig private Investitionen.",
        )

    @staticmethod
    def inflation() -> Axiom:
        """Axiom about monetary expansion causing inflation."""
        return Axiom.create(
            label="A-02",
            beschreibung="Eine starke Ausweitung der Geldmenge führt mittelfristig zu Inflation.",
        )

    @staticmethod
    def vertrauen() -> Axiom:
        """Axiom about institutional trust being a precondition for reform effectiveness."""
        return Axiom.create(
            label="A-03",
            beschreibung=(
                "Politische Reformen wirken nur dann stabilisierend, "
                "wenn ausreichendes Vertrauen in staatliche Institutionen vorhanden ist."
            ),
        )

    @staticmethod
    def collection() -> list[Axiom]:
        """Three varied axioms — for consistency checking tests."""
        return [
            AxiomMother.zins(),
            AxiomMother.inflation(),
            AxiomMother.vertrauen(),
        ]


class WirkmodellMother:
    """Factory for Wirkmodell test objects."""

    @staticmethod
    def empty() -> Wirkmodell:
        """Simplest valid Wirkmodell — no axiome."""
        return Wirkmodell.create(titel="Klartext Wirkmodell")

    @staticmethod
    def with_axiome() -> Wirkmodell:
        """Wirkmodell with three standard axioms — for consistency checking tests."""
        wm = Wirkmodell.create(titel="Klartext Wirkmodell")
        for axiom in AxiomMother.collection():
            wm.add_axiom(axiom)
        return wm

    @staticmethod
    def with_title(titel: str) -> Wirkmodell:
        """Wirkmodell with a custom title — for title-specific tests."""
        return Wirkmodell.create(titel=titel)

    @staticmethod
    def collection() -> list[Wirkmodell]:
        """Three Wirkmodelle with distinct titles — for list tests."""
        return [
            Wirkmodell.create(titel="Erstes Wirkmodell"),
            Wirkmodell.create(titel="Zweites Wirkmodell"),
            Wirkmodell.create(titel="Drittes Wirkmodell"),
        ]
