"""Service: imports a narrative from a file and delegates parsing to a NarrativeParser."""

from __future__ import annotations

from pathlib import Path

from api.exceptions.narrative import NarrativeFileNotFoundError, NarrativeParseError
from api.models.narrative import Narrative
from api.parsers.narrative_parser import NarrativeParser


class NarrativeImportService:
    """Reads a narrative file from disk and converts it into a Narrative domain object.

    The service is responsible for file I/O only. It delegates all text
    interpretation to the injected NarrativeParser.
    """

    def __init__(self, parser: NarrativeParser) -> None:
        self._parser = parser

    def import_from_file(self, path: Path) -> Narrative:
        """Reads the file at the given path and returns a populated Narrative.

        Raises NarrativeFileNotFoundError if the path does not exist.
        Raises NarrativeParseError if the file is empty or contains no parseable scenes.
        """
        if not path.exists():
            raise NarrativeFileNotFoundError(f"Narrative file not found: {path}")

        content = path.read_text(encoding="utf-8")

        if not content.strip():
            raise NarrativeParseError(f"Narrative file is empty: {path}")

        scenes = self._parser.parse(content)

        if not scenes:
            raise NarrativeParseError(f"No scenes found in narrative file: {path}")

        narrative = Narrative.create(title=path.stem)
        for scene in scenes:
            narrative.add_scene(scene)

        return narrative
