"""Port: abstract interface for narrative parsers that operate on file paths.

Used for binary formats (e.g. DOCX) where the file content cannot be read
as plain UTF-8 text and handed to a NarrativeParser.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from api.models.narrative import Scene


class NarrativeFileParser(ABC):
    """Defines the contract for turning a file into a list of Scenes.

    Implementations receive a file path and are responsible for reading
    the file and returning Scene objects.  They know nothing about
    databases or services – pure file transformation.
    """

    @abstractmethod
    def parse_file(self, path: Path) -> list[Scene]:
        """Opens the file at *path* and returns the extracted scenes."""
        ...
