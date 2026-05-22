"""FakeCausalModelRepository — in-memory CausalModelRepository for unit tests."""

from __future__ import annotations

import uuid

from api.exceptions.causal_model import CausalModelNotFoundError
from api.models.causal_model import Axiom, CausalModel
from api.repositories.causal_model_repository import CausalModelRepository


class FakeCausalModelRepository(CausalModelRepository):
    """In-memory CausalModelRepository for unit tests.

    Assigns UUID strings as IDs on save. No database involved.
    """

    def __init__(self) -> None:
        self._store: dict[str, CausalModel] = {}

    async def save(self, causal_model: CausalModel) -> CausalModel:
        """Stores the CausalModel with a generated ID and returns it with IDs assigned."""
        cm_id = str(uuid.uuid4())
        saved = CausalModel(id=cm_id, title=causal_model.title, status=causal_model.status)
        for axiom in causal_model.axioms:
            saved.add_axiom(Axiom(id=str(uuid.uuid4()), label=axiom.label, description=axiom.description))
        self._store[cm_id] = saved
        return saved

    async def add_axiom(self, causal_model_id: str, axiom: Axiom) -> Axiom:
        """Adds an Axiom to the stored CausalModel and returns it with an ID."""
        if causal_model_id not in self._store:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")
        saved_axiom = Axiom(id=str(uuid.uuid4()), label=axiom.label, description=axiom.description)
        self._store[causal_model_id].add_axiom(saved_axiom)
        return saved_axiom

    async def find_by_id(self, causal_model_id: str) -> CausalModel:
        """Returns the CausalModel with its Axioms. Raises CausalModelNotFoundError if absent."""
        if causal_model_id not in self._store:
            raise CausalModelNotFoundError(f"CausalModel not found: {causal_model_id}")
        return self._store[causal_model_id]

    async def list_all(self) -> list[CausalModel]:
        """Returns all CausalModels as title-only summaries."""
        return [CausalModel(id=cm.id, title=cm.title, status=cm.status) for cm in self._store.values()]
