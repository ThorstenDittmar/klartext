"""Port: abstract interface for narrative parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from api.models.narrative import Scene


class NarrativeParser(ABC):
    """Defines the contract for turning raw text content into a list of Scenes.

    Implementations receive a string and return Scene objects – they know
    nothing about files, databases, or services.
    """

    @abstractmethod
    def parse(self, content: str) -> list[Scene]:
        """Parses raw text content and returns the extracted scenes."""
        ...
