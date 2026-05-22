"""WirkmodellService — business logic for Wirkmodell management and consistency checking."""

from __future__ import annotations

from api.exceptions.wirkmodell import WirkmodellNotFoundError
from api.models.wirkmodell import Axiom, Wirkmodell
from api.providers.konsistenz_checker import KonsistenzChecker, KonsistenzResult
from api.repositories.wirkmodell_repository import WirkmodellRepository


class WirkmodellService:
    """Orchestrates Wirkmodell persistence and consistency checking."""

    def __init__(
        self,
        repository: WirkmodellRepository,
        konsistenz_checker: KonsistenzChecker,
    ) -> None:
        self._repository = repository
        self._checker = konsistenz_checker

    async def create(self, titel: str) -> Wirkmodell:
        """Creates and persists a new Wirkmodell."""
        wirkmodell = Wirkmodell.create(titel=titel)
        return await self._repository.save(wirkmodell)

    async def add_axiom(self, wirkmodell_id: str, label: str, beschreibung: str) -> Axiom:
        """Adds an Axiom to an existing Wirkmodell. Raises WirkmodellNotFoundError if absent."""
        await self._repository.find_by_id(wirkmodell_id)
        axiom = Axiom.create(label=label, beschreibung=beschreibung)
        return await self._repository.add_axiom(wirkmodell_id, axiom)

    async def find_by_id(self, wirkmodell_id: str) -> Wirkmodell:
        """Returns a Wirkmodell with all its Axiome. Raises WirkmodellNotFoundError if absent."""
        return await self._repository.find_by_id(wirkmodell_id)

    async def list_all(self) -> list[Wirkmodell]:
        """Returns all Wirkmodelle as title-only summaries."""
        return await self._repository.list_all()

    async def check_consistency(
        self, wirkmodell_id: str, szenen_text: str
    ) -> KonsistenzResult:
        """Checks a scene text against all Axiome of the given Wirkmodell.

        Raises WirkmodellNotFoundError if the Wirkmodell does not exist.
        Returns a KonsistenzResult with konflikte if inconsistencies are detected.
        """
        wirkmodell = await self._repository.find_by_id(wirkmodell_id)
        return await self._checker.check(szenen_text, wirkmodell.axiome)
