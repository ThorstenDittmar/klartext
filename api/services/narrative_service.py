"""Service: orchestrates narrative import and retrieval."""

from __future__ import annotations

from pathlib import Path

from api.models.narrative import Narrative
from api.repositories.narrative_repository import NarrativeRepository
from api.services.narrative_import_service import NarrativeImportService


class NarrativeService:
    """Coordinates file import and database persistence for Narratives.

    Responsibilities:
    - Delegates file reading and parsing to NarrativeImportService.
    - Delegates persistence to NarrativeRepository.
    - Provides find_by_id and list_all for read access.
    """

    def __init__(
        self,
        import_service: NarrativeImportService,
        repository: NarrativeRepository,
    ) -> None:
        self._import_service = import_service
        self._repository = repository

    async def import_from_file(self, path: Path) -> Narrative:
        """Reads, parses and persists a Narrative from the given file path.

        Returns the saved Narrative with IDs assigned to it and all its Scenes.
        Raises NarrativeFileNotFoundError if the file does not exist.
        Raises NarrativeParseError if the file is empty or contains no scenes.
        Raises NarrativePersistenceError on database failure.
        """
        narrative = self._import_service.import_from_file(path)
        return await self._repository.save(narrative)

    async def find_by_id(self, narrative_id: str) -> Narrative:
        """Returns the Narrative with the given ID, including its Scenes.

        Raises NarrativeNotFoundError if no Narrative exists for that ID.
        """
        return await self._repository.find_by_id(narrative_id)

    async def list_all(self) -> list[Narrative]:
        """Returns all persisted Narratives without their Scenes."""
        return await self._repository.list_all()
