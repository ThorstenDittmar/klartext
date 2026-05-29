"""Service: imports a narrative from a file and delegates parsing to a NarrativeParser.

Text-based formats (.md, .txt, …) are read as UTF-8 and handed to the
injected NarrativeParser.  Binary formats (e.g. .docx) require a
NarrativeFileParser registered for that suffix via *file_parsers*.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from api.exceptions.narrative import NarrativeFileNotFoundError, NarrativeParseError
from api.models.narrative import Narrative, Scene
from api.parsers.narrative_file_parser import NarrativeFileParser
from api.parsers.narrative_parser import NarrativeParser


class NarrativeImportService:
    """Reads a narrative file from disk and converts it into a Narrative domain object.

    For text formats the service reads the file content and delegates to
    the injected *parser*.  For binary formats it dispatches to the
    matching *NarrativeFileParser* from *file_parsers* (keyed by
    lower-case suffix including the dot, e.g. ``".docx"``).
    """

    def __init__(
        self,
        parser: NarrativeParser,
        file_parsers: Optional[dict[str, NarrativeFileParser]] = None,
    ) -> None:
        self._parser = parser
        self._file_parsers: dict[str, NarrativeFileParser] = file_parsers or {}

    def import_from_file(self, path: Path) -> Narrative:
        """Reads the file at the given path and returns a populated Narrative.

        Raises NarrativeFileNotFoundError if the path does not exist.
        Raises NarrativeParseError if the file is empty or contains no parseable scenes.
        """
        if not path.exists():
            raise NarrativeFileNotFoundError(f"Narrative file not found: {path}")

        suffix = path.suffix.lower()
        if suffix in self._file_parsers:
            return self._import_with_file_parser(path, self._file_parsers[suffix])

        return self._import_as_text(path)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _import_with_file_parser(
        self, path: Path, file_parser: NarrativeFileParser
    ) -> Narrative:
        """Delegates file reading and scene extraction to *file_parser*."""
        scenes = file_parser.parse_file(path)
        if not scenes:
            raise NarrativeParseError(f"No scenes found in narrative file: {path}")
        return self._build_narrative(path.stem, scenes)

    def _import_as_text(self, path: Path) -> Narrative:
        """Reads *path* as UTF-8 text and delegates to the text parser."""
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            raise NarrativeParseError(f"Narrative file is empty: {path}")
        scenes = self._parser.parse(content)
        if not scenes:
            raise NarrativeParseError(f"No scenes found in narrative file: {path}")
        return self._build_narrative(path.stem, scenes)

    @staticmethod
    def _build_narrative(title: str, scenes: list[Scene]) -> Narrative:
        """Creates a Narrative from a title and a list of already-parsed scenes."""
        narrative = Narrative.create(title=title)
        for scene in scenes:
            narrative.add_scene(scene)
        return narrative
