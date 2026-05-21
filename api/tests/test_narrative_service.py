"""Tests for NarrativeService.

NarrativeService orchestrates two collaborators:
  1. NarrativeImportService – reads a file from disk and parses it.
  2. NarrativeRepository – persists and retrieves Narratives.

Tests inject a FakeNarrativeParser (so no Markdown parsing happens) and a
FakeNarrativeRepository (so no database is involved).
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from api.exceptions.narrative import NarrativeFileNotFoundError, NarrativeNotFoundError
from api.models.narrative import Narrative, Scene
from api.parsers.narrative_parser import NarrativeParser
from api.repositories.narrative_repository import NarrativeRepository
from api.services.narrative_import_service import NarrativeImportService
from api.services.narrative_service import NarrativeService

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "klartext-eine-geschichte-ueber-eine-geschichte"
    / "narrative.md"
)

NONEXISTENT_PATH = Path("/tmp/does_not_exist/narrative.md")


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeNarrativeParser(NarrativeParser):
    """Returns two fixed scenes regardless of content."""

    def parse(self, content: str) -> list[Scene]:
        return [
            Scene.create(title="Szene 1", text="Fake text.", position=1),
            Scene.create(title="Szene 2", text="Auch fake.", position=2),
        ]


class FakeNarrativeRepository(NarrativeRepository):
    """In-memory NarrativeRepository for unit tests."""

    def __init__(self) -> None:
        self._store: dict[str, Narrative] = {}

    async def save(self, narrative: Narrative) -> Narrative:
        """Stores the narrative with a generated ID."""
        narrative_id = str(uuid.uuid4())
        saved = Narrative(id=narrative_id, title=narrative.title)
        for scene in narrative.scenes:
            saved.add_scene(
                Scene(
                    id=str(uuid.uuid4()),
                    title=scene.title,
                    text=scene.text,
                    position=scene.position,
                )
            )
        self._store[narrative_id] = saved
        return saved

    async def find_by_id(self, narrative_id: str) -> Narrative:
        if narrative_id not in self._store:
            raise NarrativeNotFoundError(f"Narrative not found: {narrative_id}")
        return self._store[narrative_id]

    async def list_all(self) -> list[Narrative]:
        return [Narrative(id=n.id, title=n.title) for n in self._store.values()]


def make_service(
    parser: NarrativeParser | None = None,
    repository: NarrativeRepository | None = None,
) -> NarrativeService:
    return NarrativeService(
        import_service=NarrativeImportService(parser=parser or FakeNarrativeParser()),
        repository=repository or FakeNarrativeRepository(),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_import_returns_narrative_with_id() -> None:
    """Expects import_from_file to return a Narrative with a non-None ID after saving."""
    service = make_service()

    narrative = await service.import_from_file(FIXTURE_PATH)

    assert narrative.id is not None


@pytest.mark.asyncio
async def test_narrative_service_import_returns_narrative_with_scenes() -> None:
    """Expects the returned Narrative to contain the scenes produced by the parser."""
    service = make_service()

    narrative = await service.import_from_file(FIXTURE_PATH)

    assert len(narrative.scenes) == 2


@pytest.mark.asyncio
async def test_narrative_service_import_assigns_ids_to_scenes() -> None:
    """Expects each scene in the saved Narrative to have a non-None ID."""
    service = make_service()

    narrative = await service.import_from_file(FIXTURE_PATH)

    assert all(scene.id is not None for scene in narrative.scenes)


@pytest.mark.asyncio
async def test_narrative_service_find_by_id_returns_saved_narrative() -> None:
    """Expects find_by_id to return the Narrative that was previously imported."""
    service = make_service()
    saved = await service.import_from_file(FIXTURE_PATH)

    found = await service.find_by_id(saved.id)  # type: ignore[arg-type]

    assert found.id == saved.id
    assert len(found.scenes) == 2


@pytest.mark.asyncio
async def test_narrative_service_list_all_includes_imported_narrative() -> None:
    """Expects list_all to contain the Narrative after it has been imported."""
    service = make_service()
    saved = await service.import_from_file(FIXTURE_PATH)

    all_narratives = await service.list_all()

    ids = [n.id for n in all_narratives]
    assert saved.id in ids


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_narrative_service_import_raises_for_nonexistent_file() -> None:
    """Expects NarrativeFileNotFoundError when the given path does not exist."""
    service = make_service()

    with pytest.raises(NarrativeFileNotFoundError):
        await service.import_from_file(NONEXISTENT_PATH)


@pytest.mark.asyncio
async def test_narrative_service_find_by_id_raises_for_unknown_id() -> None:
    """Expects NarrativeNotFoundError when no Narrative exists for the given ID."""
    service = make_service()

    with pytest.raises(NarrativeNotFoundError):
        await service.find_by_id("00000000-0000-0000-0000-000000000000")
