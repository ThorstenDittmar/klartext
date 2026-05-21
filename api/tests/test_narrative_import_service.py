"""Tests for NarrativeImportService.

The NarrativeImportService is responsible for exactly two things:
  1. Reading the raw file content from disk.
  2. Handing that content to a NarrativeParser and wrapping the result
     in a Narrative domain object.

It knows nothing about Markdown syntax – that is the parser's concern.
The FakeNarrativeParser below lets us test the service in isolation,
without depending on the real parser's correctness.
"""

from pathlib import Path

import pytest

from api.exceptions.narrative import NarrativeFileNotFoundError, NarrativeParseError
from api.models.narrative import Scene
from api.parsers.narrative_parser import NarrativeParser
from api.services.narrative_import_service import NarrativeImportService

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "klartext-eine-geschichte-ueber-eine-geschichte"
    / "narrative.md"
)

NONEXISTENT_PATH = Path("/tmp/does_not_exist/narrative.md")


class FakeNarrativeParser(NarrativeParser):
    """Records the content it receives so tests can inspect it."""

    def __init__(self) -> None:
        self.received_content: str | None = None

    def parse(self, content: str) -> list[Scene]:
        self.received_content = content
        return [
            Scene.create(title="Szene 1", text="Fake text.", position=1),
            Scene.create(title="Szene 2", text="Auch fake.", position=2),
        ]


class FakeParserReturnsNothing(NarrativeParser):
    """Simulates a parser that finds no scenes – e.g. because the content is nonsense."""

    def parse(self, content: str) -> list[Scene]:
        return []


# --- Happy path ---


def test_narrative_import_service_passes_file_content_to_parser() -> None:
    """Expects the parser to receive the file content – not None and not empty."""
    parser = FakeNarrativeParser()
    service = NarrativeImportService(parser=parser)

    service.import_from_file(FIXTURE_PATH)

    assert parser.received_content is not None
    assert len(parser.received_content) > 0


def test_narrative_import_service_passes_actual_fixture_content_to_parser() -> None:
    """Expects the parser to receive the real file content, not a placeholder."""
    parser = FakeNarrativeParser()
    service = NarrativeImportService(parser=parser)

    service.import_from_file(FIXTURE_PATH)

    assert "Klartext" in parser.received_content  # type: ignore[operator]


def test_narrative_import_service_returns_narrative_with_scenes_from_parser() -> None:
    """Expects the returned Narrative to contain exactly the scenes the parser produced."""
    parser = FakeNarrativeParser()
    service = NarrativeImportService(parser=parser)

    narrative = service.import_from_file(FIXTURE_PATH)

    assert len(narrative.scenes) == 2


def test_narrative_import_service_with_real_parser_creates_scenes_from_fixture() -> None:
    """Expects the full chain (service + real parser + fixture) to produce non-empty scenes."""
    from api.parsers.markdown_narrative_parser import MarkdownNarrativeParser

    parser = MarkdownNarrativeParser()
    service = NarrativeImportService(parser=parser)

    narrative = service.import_from_file(FIXTURE_PATH)

    assert len(narrative.scenes) > 0
    assert all(scene.text for scene in narrative.scenes)


# --- Error cases ---


def test_narrative_import_service_raises_for_nonexistent_file() -> None:
    """Expects a NarrativeFileNotFoundError when the given path does not exist."""
    service = NarrativeImportService(parser=FakeNarrativeParser())

    with pytest.raises(NarrativeFileNotFoundError):
        service.import_from_file(NONEXISTENT_PATH)


def test_narrative_import_service_raises_for_wrong_filename_in_fixture_directory() -> None:
    """Expects a NarrativeFileNotFoundError when the directory exists but the file name is wrong."""
    wrong_path = FIXTURE_PATH.parent / "typo_narrative.md"
    service = NarrativeImportService(parser=FakeNarrativeParser())

    with pytest.raises(NarrativeFileNotFoundError):
        service.import_from_file(wrong_path)


def test_narrative_import_service_raises_for_empty_file(tmp_path: Path) -> None:
    """Expects a NarrativeParseError when the file exists but contains no content at all."""
    empty_file = tmp_path / "narrative.md"
    empty_file.write_text("")
    service = NarrativeImportService(parser=FakeNarrativeParser())

    with pytest.raises(NarrativeParseError):
        service.import_from_file(empty_file)


def test_narrative_import_service_raises_for_file_with_no_parseable_scenes(tmp_path: Path) -> None:
    """Expects a NarrativeParseError when the file has content but the parser finds no scenes."""
    nonsense_file = tmp_path / "narrative.md"
    nonsense_file.write_text("Das hier ist kein gültiges Narrativ-Format.")
    service = NarrativeImportService(parser=FakeParserReturnsNothing())

    with pytest.raises(NarrativeParseError):
        service.import_from_file(nonsense_file)
