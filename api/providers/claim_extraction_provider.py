"""Port: abstract interface for claim extraction providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.claim import Claim
from api.models.narrative import Scene


class ClaimExtractionProvider(ABC):
    """Defines the contract for extracting Claims from a Scene.

    Implementations may call an LLM API, a local model, or any other
    extraction strategy – the service knows only this interface.
    """

    @abstractmethod
    async def extract(self, scene: Scene) -> list[Claim]:
        """Extracts claims from the given scene and returns them as a list."""
        ...
