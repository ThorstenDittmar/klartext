"""CausalModelService — business logic for CausalModel management and consistency checking."""

from __future__ import annotations

from api.exceptions.causal_model import CausalModelNotFoundError
from api.models.causal_model import Axiom, CausalModel
from api.providers.consistency_checker import ConsistencyChecker, ConsistencyResult
from api.repositories.causal_model_repository import CausalModelRepository


class CausalModelService:
    """Orchestrates CausalModel persistence and consistency checking."""

    def __init__(
        self,
        repository: CausalModelRepository,
        consistency_checker: ConsistencyChecker,
    ) -> None:
        self._repository = repository
        self._checker = consistency_checker

    async def create(self, title: str) -> CausalModel:
        """Creates and persists a new CausalModel."""
        causal_model = CausalModel.create(title=title)
        return await self._repository.save(causal_model)

    async def add_axiom(self, causal_model_id: str, label: str, description: str) -> Axiom:
        """Adds an Axiom to an existing CausalModel. Raises CausalModelNotFoundError if absent."""
        await self._repository.find_by_id(causal_model_id)
        axiom = Axiom.create(label=label, description=description)
        return await self._repository.add_axiom(causal_model_id, axiom)

    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Returns a CausalModel with all its Axioms. Raises CausalModelNotFoundError if absent."""
        return await self._repository.find_by_id(causal_model_id)

    async def list_all(self) -> list[CausalModel]:
        """Returns all CausalModels as title-only summaries."""
        return await self._repository.list_all()

    async def check_consistency(
        self, causal_model_id: str, scene_text: str
    ) -> ConsistencyResult:
        """Checks a scene text against all Axioms of the given CausalModel.

        Raises CausalModelNotFoundError if the CausalModel does not exist.
        Returns a ConsistencyResult with conflicts if inconsistencies are detected.
        """
        causal_model = await self._repository.find_by_id(causal_model_id)
        return await self._checker.check(scene_text, causal_model.axioms)
