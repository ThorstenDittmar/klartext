"""Service that builds the debug object graph for a given user.

Collects all domain objects reachable from the user (Narratives, Scenes,
Actors, Claims, CausalModels, Slots, Relations, Axioms) and returns them
as a flat list of nodes and directed edges for the frontend graph renderer.
"""

from __future__ import annotations

import logging

from api.exceptions.causal_model import CausalModelNotFoundError
from api.models.causal_model import CausalRelation
from api.repositories.causal_model_repository import CausalModelRepository
from api.repositories.claim_repository import ClaimRepository
from api.repositories.narrative_repository import NarrativeRepository
from api.repositories.user_repository import UserRepository
from api.schemas.debug import DebugEdge, DebugGraphResponse, DebugNode


class DebugGraphService:
    """Builds a full object graph of all domain objects owned by a given user."""

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        user_repository: UserRepository,
        narrative_repository: NarrativeRepository,
        claim_repository: ClaimRepository,
        causal_model_repository: CausalModelRepository,
    ) -> None:
        self._user_repo = user_repository
        self._narrative_repo = narrative_repository
        self._claim_repo = claim_repository
        self._causal_model_repo = causal_model_repository

    async def build_graph(self, user_id: str) -> DebugGraphResponse:
        """Builds and returns the full object graph for the given user.

        Traverses User → Narratives → Scenes/Actors/Claims → CausalModels
        → Slots/Relations/Axioms and represents each domain object as a node
        with all its field values, and each reference as a directed edge.
        """
        self.logger.debug("DebugGraphService.build_graph: user_id=%s", user_id)
        nodes: list[DebugNode] = []
        edges: list[DebugEdge] = []

        # ── User ─────────────────────────────────────────────────────────────
        user = await self._user_repo.find_by_id(user_id)
        user_node_id = f"user-{user.id}"
        nodes.append(
            DebugNode(
                id=user_node_id,
                class_name="User",
                fields={"id": str(user.id), "name": user.name},
            )
        )

        # ── Narratives ────────────────────────────────────────────────────────
        narratives = await self._narrative_repo.list_for_user(user_id)
        seen_causal_model_ids: set[str] = set()

        for narrative in narratives:
            # Reload full narrative to get scenes and actors
            full_narrative = await self._narrative_repo.find_by_id(
                narrative.id  # type: ignore[arg-type]
            )
            narrative_node_id = f"narrative-{narrative.id}"

            nodes.append(
                DebugNode(
                    id=narrative_node_id,
                    class_name="Narrative",
                    fields={
                        "id": str(narrative.id),
                        "title": narrative.title,
                        "causal_model_id": narrative.causal_model_id,
                    },
                )
            )
            edges.append(
                DebugEdge(
                    id=f"edge-user-narrative-{narrative.id}",
                    source=user_node_id,
                    target=narrative_node_id,
                    label="narratives",
                )
            )

            # ── Scenes ───────────────────────────────────────────────────────
            for scene in full_narrative.scenes:
                scene_node_id = f"scene-{scene.id}"
                text_preview = scene.text[:80] + "…" if len(scene.text) > 80 else scene.text
                nodes.append(
                    DebugNode(
                        id=scene_node_id,
                        class_name="Scene",
                        fields={
                            "id": str(scene.id),
                            "title": scene.title,
                            "position": scene.position,
                            "text": text_preview,
                        },
                    )
                )
                edges.append(
                    DebugEdge(
                        id=f"edge-narrative-scene-{scene.id}",
                        source=narrative_node_id,
                        target=scene_node_id,
                        label="scenes",
                    )
                )

            # ── Actors ───────────────────────────────────────────────────────
            for actor in full_narrative.actors:
                actor_node_id = f"actor-{actor.id}"
                nodes.append(
                    DebugNode(
                        id=actor_node_id,
                        class_name="Actor",
                        fields={
                            "id": str(actor.id),
                            "label": actor.label,
                            "actor_type": actor.actor_type,
                            "entity_ref": actor.entity_ref,
                            "notes": actor.notes,
                        },
                    )
                )
                edges.append(
                    DebugEdge(
                        id=f"edge-narrative-actor-{actor.id}",
                        source=narrative_node_id,
                        target=actor_node_id,
                        label="actors",
                    )
                )

            # ── Claims ───────────────────────────────────────────────────────
            claims = await self._claim_repo.find_by_narrative_id(
                narrative.id  # type: ignore[arg-type]
            )
            for claim in claims:
                claim_node_id = f"claim-{claim.id}"
                nodes.append(
                    DebugNode(
                        id=claim_node_id,
                        class_name="Claim",
                        fields={
                            "id": str(claim.id),
                            "label": claim.label,
                            "typ": str(claim.typ),
                            "status": claim.status.value,
                            "confidence": claim.confidence,
                        },
                    )
                )
                edges.append(
                    DebugEdge(
                        id=f"edge-narrative-claim-{claim.id}",
                        source=narrative_node_id,
                        target=claim_node_id,
                        label="claims",
                    )
                )

            # ── CausalModel ──────────────────────────────────────────────────
            if narrative.causal_model_id and narrative.causal_model_id not in seen_causal_model_ids:
                seen_causal_model_ids.add(narrative.causal_model_id)
                try:
                    causal_model = await self._causal_model_repo.find_by_id(
                        narrative.causal_model_id
                    )
                except CausalModelNotFoundError:
                    self.logger.debug(
                        "DebugGraphService.build_graph: dangling causal_model_id=%s, skipping",
                        narrative.causal_model_id,
                    )
                    continue

                cm_node_id = f"causal-model-{causal_model.id}"
                nodes.append(
                    DebugNode(
                        id=cm_node_id,
                        class_name="CausalModel",
                        fields={
                            "id": str(causal_model.id),
                            "title": causal_model.title,
                            "status": str(causal_model.status),
                        },
                    )
                )
                edges.append(
                    DebugEdge(
                        id=f"edge-narrative-causalmodel-{narrative.id}",
                        source=narrative_node_id,
                        target=cm_node_id,
                        label="causal_model",
                    )
                )

                # Axioms
                for axiom in causal_model.axioms:
                    axiom_node_id = f"axiom-{axiom.id}"
                    nodes.append(
                        DebugNode(
                            id=axiom_node_id,
                            class_name="Axiom",
                            fields={
                                "id": str(axiom.id),
                                "label": axiom.label,
                                "description": axiom.description,
                            },
                        )
                    )
                    edges.append(
                        DebugEdge(
                            id=f"edge-causalmodel-axiom-{axiom.id}",
                            source=cm_node_id,
                            target=axiom_node_id,
                            label="axioms",
                        )
                    )

                # Slots
                for slot in causal_model.get_slots():
                    slot_node_id = f"slot-{slot.id}"
                    nodes.append(
                        DebugNode(
                            id=slot_node_id,
                            class_name="Slot",
                            fields={
                                "id": str(slot.id),
                                "identifier": slot.identifier,
                                "slot_type": str(slot.slot_type),
                                "epistemic_status": str(slot.epistemic_status),
                            },
                        )
                    )
                    edges.append(
                        DebugEdge(
                            id=f"edge-causalmodel-slot-{slot.id}",
                            source=cm_node_id,
                            target=slot_node_id,
                            label="slots",
                        )
                    )

                # Relations — CausalRelation has polarity; DefinitoryRelation
                # does not, so we discriminate via isinstance before accessing it.
                for relation in causal_model.get_relations():
                    relation_node_id = f"relation-{relation.id}"
                    fields: dict[str, object] = {
                        "id": str(relation.id),
                        "identifier": relation.identifier,
                        "epistemic_status": str(relation.epistemic_status),
                    }
                    if isinstance(relation, CausalRelation):
                        fields["polarity"] = str(relation.polarity)
                    nodes.append(
                        DebugNode(
                            id=relation_node_id,
                            class_name="CausalRelation",
                            fields=fields,
                        )
                    )
                    edges.append(
                        DebugEdge(
                            id=f"edge-causalmodel-relation-{relation.id}",
                            source=cm_node_id,
                            target=relation_node_id,
                            label="relations",
                        )
                    )

        return DebugGraphResponse(nodes=nodes, edges=edges)
