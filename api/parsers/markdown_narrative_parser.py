"""Adapter: parses Markdown-formatted narrative text into Scene objects.

Convention: scenes are introduced by a level-3 heading (### Szene N).
Everything before the first such heading (title, subtitle, preamble)
is ignored. Horizontal rules (---) used as scene separators are stripped
from the extracted text.
"""

from __future__ import annotations

import re

from api.models.narrative import Scene
from api.parsers.narrative_parser import NarrativeParser

_SCENE_HEADING = re.compile(r"^###\s+(.+)$", re.MULTILINE)
_HORIZONTAL_RULE = re.compile(r"^\s*---\s*$", re.MULTILINE)


class MarkdownNarrativeParser(NarrativeParser):
    """Parses Markdown text into Scene objects based on ### headings."""

    def parse(self, content: str) -> list[Scene]:
        """Splits content on ### headings and returns one Scene per heading."""
        if not content.strip():
            return []

        matches = list(_SCENE_HEADING.finditer(content))
        if not matches:
            return []

        scenes: list[Scene] = []
        for position, match in enumerate(matches, start=1):
            title = match.group(1).strip()
            start = match.end()
            end = matches[position].start() if position < len(matches) else len(content)

            raw_text = content[start:end]
            text = _HORIZONTAL_RULE.sub("", raw_text).strip()

            if not text:
                continue  # skip scenes with a heading but no body text

            scenes.append(Scene.create(title=title, text=text, position=position))

        return scenes
