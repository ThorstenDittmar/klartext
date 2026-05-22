"""CausalModelMother and AxiomMother — build CausalModel test objects."""

from __future__ import annotations

from api.models.causal_model import Axiom, CausalModel


class AxiomMother:
    """Factory for Axiom test objects."""

    @staticmethod
    def interest_rate() -> Axiom:
        """Axiom about interest rates dampening investment — canonical example from the spec."""
        return Axiom.create(
            label="A-01",
            description="Drastische Zinserhöhungen dämpfen kurzfristig private Investitionen.",
        )

    @staticmethod
    def inflation() -> Axiom:
        """Axiom about monetary expansion causing inflation."""
        return Axiom.create(
            label="A-02",
            description="Eine starke Ausweitung der Geldmenge führt mittelfristig zu Inflation.",
        )

    @staticmethod
    def institutional_trust() -> Axiom:
        """Axiom about institutional trust being a precondition for reform effectiveness."""
        return Axiom.create(
            label="A-03",
            description=(
                "Politische Reformen wirken nur dann stabilisierend, "
                "wenn ausreichendes Vertrauen in staatliche Institutionen vorhanden ist."
            ),
        )

    @staticmethod
    def collection() -> list[Axiom]:
        """Three varied axioms — for consistency checking tests."""
        return [
            AxiomMother.interest_rate(),
            AxiomMother.inflation(),
            AxiomMother.institutional_trust(),
        ]


class CausalModelMother:
    """Factory for CausalModel test objects."""

    @staticmethod
    def empty() -> CausalModel:
        """Simplest valid CausalModel — no axioms."""
        return CausalModel.create(title="Klartext Wirkmodell")

    @staticmethod
    def with_axioms() -> CausalModel:
        """CausalModel with three standard axioms — for consistency checking tests."""
        cm = CausalModel.create(title="Klartext Wirkmodell")
        for axiom in AxiomMother.collection():
            cm.add_axiom(axiom)
        return cm

    @staticmethod
    def with_title(title: str) -> CausalModel:
        """CausalModel with a custom title — for title-specific tests."""
        return CausalModel.create(title=title)

    @staticmethod
    def collection() -> list[CausalModel]:
        """Three CausalModels with distinct titles — for list tests."""
        return [
            CausalModel.create(title="Erstes Wirkmodell"),
            CausalModel.create(title="Zweites Wirkmodell"),
            CausalModel.create(title="Drittes Wirkmodell"),
        ]
