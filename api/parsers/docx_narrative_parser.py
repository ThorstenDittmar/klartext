"""Adapter: parses a DOCX file into Scene objects.

Convention: scene boundaries are plain-text paragraphs whose stripped
text matches the pattern "Szene <number>" exactly (e.g. "Szene 1",
"Szene 2", "Szene 10").  Paragraphs before the first scene marker are
treated as preamble and discarded.  Empty paragraphs within a scene
body are silently dropped.  The resulting scene text is the non-empty
body paragraphs joined with double newlines, stripped of surrounding
whitespace.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document

from api.models.narrative import Scene
from api.parsers.narrative_file_parser import NarrativeFileParser

# Matches exactly "Szene" followed by one or more whitespace characters
# and one or more digits – nothing else (full-string match via anchors).
_SCENE_MARKER = re.compile(r"^Szene\s+\d+$")


class DocxNarrativeParser(NarrativeFileParser):
    """Parses a DOCX file into Scene objects based on plain-text scene markers."""

    def parse_file(self, path: Path) -> list[Scene]:
        """Opens the DOCX at *path* and returns one Scene per scene marker.

        Raises FileNotFoundError when the path does not exist.
        Returns an empty list when the document contains no scene markers.
        """
        if not path.exists():
            raise FileNotFoundError(f"DOCX file not found: {path}")

        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs]

        return self._extract_scenes(paragraphs)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_scenes(self, paragraphs: list[str]) -> list[Scene]:
        """Splits *paragraphs* on scene markers and builds Scene objects."""
        # Collect (marker_text, body_paragraphs) pairs
        sections: list[tuple[str, list[str]]] = []
        current_title: str | None = None
        current_body: list[str] = []

        for text in paragraphs:
            stripped = text.strip()
            if _SCENE_MARKER.match(stripped):
                # Flush the previous section (if any)
                if current_title is not None:
                    sections.append((current_title, current_body))
                current_title = stripped
                current_body = []
            elif current_title is not None and stripped:
                # Non-empty paragraph inside a scene
                current_body.append(stripped)

        # Flush the final section
        if current_title is not None:
            sections.append((current_title, current_body))

        scenes: list[Scene] = []
        position = 1
        for title, body in sections:
            if not body:
                continue  # skip scenes with no body text
            scene_text = "\n\n".join(body)
            scenes.append(Scene.create(title=title, text=scene_text, position=position))
            position += 1

        return scenes
