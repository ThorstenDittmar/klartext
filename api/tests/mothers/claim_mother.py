"""ClaimMother — builds Claim test objects for all test scenarios."""

from __future__ import annotations

from api.models.claim import Claim, ClaimType


class ClaimMother:
    """Factory for Claim test objects.

    Use causal() or empirical() for single-claim tests.
    Use collection() for tests that need a varied set of claims.
    """

    @staticmethod
    def causal() -> Claim:
        """A single causal claim with high confidence."""
        return Claim.create(
            label="Money supply causes inflation",
            text="Inflation entsteht durch eine Ausweitung der Geldmenge.",
            typ=ClaimType.CAUSAL,
            confidence=0.9,
        )

    @staticmethod
    def empirical() -> Claim:
        """A single empirical claim with moderate confidence."""
        return Claim.create(
            label="2022 inflation rate above 7%",
            text="Die Inflationsrate lag 2022 bei über 7 Prozent.",
            typ=ClaimType.EMPIRICAL,
            confidence=0.8,
        )

    @staticmethod
    def normative() -> Claim:
        """A single normative claim — for tests that distinguish claim types."""
        return Claim.create(
            label="State should cap energy prices",
            text="Der Staat sollte die Energiepreise deckeln.",
            typ=ClaimType.NORMATIVE,
            confidence=0.75,
        )

    @staticmethod
    def with_low_confidence() -> Claim:
        """A claim with low confidence — for confidence boundary tests."""
        return Claim.create(
            label="Inflation may decline by 2025",
            text="Möglicherweise wird die Inflation bis 2025 sinken.",
            typ=ClaimType.PROGNOSTIC,
            confidence=0.3,
        )

    @staticmethod
    def collection() -> list[Claim]:
        """A varied set of claims covering different types — for extraction and storage tests."""
        return [
            ClaimMother.causal(),
            ClaimMother.empirical(),
            ClaimMother.normative(),
        ]
