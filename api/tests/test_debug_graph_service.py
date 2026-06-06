"""Tests for DebugGraphService.

Verifies that build_graph() produces the correct nodes and edges
for all domain objects reachable from the default user.
Uses only fake repositories — no database or API calls.
"""

from __future__ import annotations

import pytest

from api.models.claim import Claim, ClaimStatus, ClaimType
from api.models.narrative import Actor, Narrative, Scene
from api.services.debug_graph_service import DebugGraphService
from tests.fakes.fake_causal_model_repository import FakeCausalModelRepository
from tests.fakes.fake_claim_repository import FakeClaimRepository
from tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from tests.fakes.fake_user_repository import DEFAULT_USER_ID, FakeUserRepository

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _make_service_with_narrative(
    with_scene: bool = False,
    with_actor: bool = False,
    with_claim: bool = False,
) -> tuple[DebugGraphService, str, str]:
    """Sets up a service with one saved narrative and optional scene/actor/claim.

    Returns (service, user_id, narrative_id).
    """
    user_repo = FakeUserRepository()
    narrative_repo = FakeNarrativeRepository()
    claim_repo = FakeClaimRepository()
    causal_model_repo = FakeCausalModelRepository()

    base = Narrative(id=None, title="Test Narrativ", user_id=DEFAULT_USER_ID)
    if with_scene:
        base.add_scene(Scene(id=None, title="Szene 1", text="Szenentext", position=1))
    saved = await narrative_repo.save(base)

    if with_actor:
        await narrative_repo.add_actor(
            saved.id,  # type: ignore[arg-type]
            Actor(id=None, label="Maria", actor_type="individual", notes=None),
        )

    if with_claim:
        claim = Claim(
            id=None,
            label="Geld regiert die Welt",
            text="Monetäre Anreize dominieren politische Entscheidungen.",
            typ=ClaimType.CAUSAL,
            confidence=0.8,
            status=ClaimStatus.DRAFT,
        )
        await claim_repo.save_for_narrative([claim], saved.id)  # type: ignore[arg-type]

    service = DebugGraphService(
        user_repository=user_repo,
        narrative_repository=narrative_repo,
        claim_repository=claim_repo,
        causal_model_repository=causal_model_repo,
    )
    return service, DEFAULT_USER_ID, saved.id  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# User node
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_debug_graph_includes_user_node() -> None:
    """Expects a User node with class_name='User' and the correct id and name."""
    service, user_id, _ = await _make_service_with_narrative()
    graph = await service.build_graph(user_id)

    user_nodes = [n for n in graph.nodes if n.class_name == "User"]
    assert len(user_nodes) == 1
    assert user_nodes[0].fields["id"] == user_id
    assert user_nodes[0].fields["name"] == "Thorsten"


# ---------------------------------------------------------------------------
# Narrative node + edge
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_debug_graph_includes_narrative_node() -> None:
    """Expects a Narrative node with title and id for each user narrative."""
    service, user_id, narrative_id = await _make_service_with_narrative()
    graph = await service.build_graph(user_id)

    narrative_nodes = [n for n in graph.nodes if n.class_name == "Narrative"]
    assert len(narrative_nodes) == 1
    assert narrative_nodes[0].fields["id"] == narrative_id
    assert narrative_nodes[0].fields["title"] == "Test Narrativ"


@pytest.mark.asyncio
async def test_debug_graph_creates_user_to_narrative_edge() -> None:
    """Expects an edge with label 'narratives' from User to Narrative."""
    service, user_id, _ = await _make_service_with_narrative()
    graph = await service.build_graph(user_id)

    user_node_id = next(n.id for n in graph.nodes if n.class_name == "User")
    narrative_node_id = next(n.id for n in graph.nodes if n.class_name == "Narrative")
    edge = next(
        (e for e in graph.edges if e.source == user_node_id and e.target == narrative_node_id),
        None,
    )
    assert edge is not None
    assert edge.label == "narratives"


# ---------------------------------------------------------------------------
# Scene node + edge
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_debug_graph_includes_scene_nodes() -> None:
    """Expects a Scene node for each scene in the narrative."""
    service, user_id, _ = await _make_service_with_narrative(with_scene=True)
    graph = await service.build_graph(user_id)

    scene_nodes = [n for n in graph.nodes if n.class_name == "Scene"]
    assert len(scene_nodes) == 1
    assert scene_nodes[0].fields["title"] == "Szene 1"


@pytest.mark.asyncio
async def test_debug_graph_creates_narrative_to_scene_edge() -> None:
    """Expects an edge with label 'scenes' from Narrative to Scene."""
    service, user_id, _ = await _make_service_with_narrative(with_scene=True)
    graph = await service.build_graph(user_id)

    narrative_node_id = next(n.id for n in graph.nodes if n.class_name == "Narrative")
    scene_node_id = next(n.id for n in graph.nodes if n.class_name == "Scene")
    edge = next(
        (e for e in graph.edges if e.source == narrative_node_id and e.target == scene_node_id),
        None,
    )
    assert edge is not None
    assert edge.label == "scenes"


# ---------------------------------------------------------------------------
# Actor node + edge
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_debug_graph_includes_actor_nodes() -> None:
    """Expects an Actor node with label and actor_type for each narrative actor."""
    service, user_id, _ = await _make_service_with_narrative(with_actor=True)
    graph = await service.build_graph(user_id)

    actor_nodes = [n for n in graph.nodes if n.class_name == "Actor"]
    assert len(actor_nodes) == 1
    assert actor_nodes[0].fields["label"] == "Maria"
    assert actor_nodes[0].fields["actor_type"] == "individual"


@pytest.mark.asyncio
async def test_debug_graph_creates_narrative_to_actor_edge() -> None:
    """Expects an edge with label 'actors' from Narrative to Actor."""
    service, user_id, _ = await _make_service_with_narrative(with_actor=True)
    graph = await service.build_graph(user_id)

    narrative_node_id = next(n.id for n in graph.nodes if n.class_name == "Narrative")
    actor_node_id = next(n.id for n in graph.nodes if n.class_name == "Actor")
    edge = next(
        (e for e in graph.edges if e.source == narrative_node_id and e.target == actor_node_id),
        None,
    )
    assert edge is not None
    assert edge.label == "actors"


# ---------------------------------------------------------------------------
# Claim node + edge
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_debug_graph_includes_claim_nodes() -> None:
    """Expects a Claim node with label and typ for each narrative claim."""
    service, user_id, _ = await _make_service_with_narrative(with_claim=True)
    graph = await service.build_graph(user_id)

    claim_nodes = [n for n in graph.nodes if n.class_name == "Claim"]
    assert len(claim_nodes) == 1
    assert claim_nodes[0].fields["label"] == "Geld regiert die Welt"
    assert claim_nodes[0].fields["typ"] == "causal"


@pytest.mark.asyncio
async def test_debug_graph_creates_narrative_to_claim_edge() -> None:
    """Expects an edge with label 'claims' from Narrative to Claim."""
    service, user_id, _ = await _make_service_with_narrative(with_claim=True)
    graph = await service.build_graph(user_id)

    narrative_node_id = next(n.id for n in graph.nodes if n.class_name == "Narrative")
    claim_node_id = next(n.id for n in graph.nodes if n.class_name == "Claim")
    edge = next(
        (e for e in graph.edges if e.source == narrative_node_id and e.target == claim_node_id),
        None,
    )
    assert edge is not None
    assert edge.label == "claims"


# ---------------------------------------------------------------------------
# Empty graph
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_debug_graph_only_user_node_when_no_narratives() -> None:
    """Expects only a User node when the user has no narratives."""
    user_repo = FakeUserRepository()
    service = DebugGraphService(
        user_repository=user_repo,
        narrative_repository=FakeNarrativeRepository(),
        claim_repository=FakeClaimRepository(),
        causal_model_repository=FakeCausalModelRepository(),
    )

    graph = await service.build_graph(DEFAULT_USER_ID)

    assert len(graph.nodes) == 1
    assert graph.nodes[0].class_name == "User"
    assert graph.edges == []
