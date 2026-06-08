"""Tests for the debug router.

Covers GET /debug/health and GET /debug/object-graph.
Uses a stub DebugGraphService backed by FakeUserRepository
to avoid any database or Supabase calls.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_debug_graph_service, get_user_service
from api.main import app
from api.services.debug_graph_service import DebugGraphService
from api.tests.fakes.fake_causal_model_repository import FakeCausalModelRepository
from api.tests.fakes.fake_claim_repository import FakeClaimRepository
from api.tests.fakes.fake_narrative_repository import FakeNarrativeRepository
from api.tests.fakes.fake_user_repository import DEFAULT_USER_ID, FakeUserRepository
from api.tests.fakes.fake_user_service import FakeUserService

# ---------------------------------------------------------------------------
# Stub service
# ---------------------------------------------------------------------------


def make_debug_graph_service() -> DebugGraphService:
    """Returns a DebugGraphService backed by empty in-memory fakes."""
    return DebugGraphService(
        user_repository=FakeUserRepository(),
        narrative_repository=FakeNarrativeRepository(),
        claim_repository=FakeClaimRepository(),
        causal_model_repository=FakeCausalModelRepository(),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def override_debug_service():
    """Replaces DebugGraphService and UserService with fakes for every test in this module."""
    app.dependency_overrides[get_debug_graph_service] = make_debug_graph_service
    app.dependency_overrides[get_user_service] = lambda: FakeUserService()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


def test_debug_health_returns_200() -> None:
    """Expects GET /debug/health to return HTTP 200 with status ok."""
    response = client.get("/debug/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Object graph endpoint
# ---------------------------------------------------------------------------


def test_debug_object_graph_returns_200() -> None:
    """Expects GET /debug/object-graph to return HTTP 200."""
    response = client.get("/debug/object-graph")
    assert response.status_code == 200


def test_debug_object_graph_returns_nodes_and_edges() -> None:
    """Expects the response to have top-level 'nodes' and 'edges' arrays."""
    response = client.get("/debug/object-graph")
    body = response.json()
    assert "nodes" in body
    assert "edges" in body
    assert isinstance(body["nodes"], list)
    assert isinstance(body["edges"], list)


def test_debug_object_graph_includes_user_node() -> None:
    """Expects at least one User node for the default user in the response."""
    response = client.get("/debug/object-graph")
    nodes = response.json()["nodes"]
    user_nodes = [n for n in nodes if n["class_name"] == "User"]
    assert len(user_nodes) == 1
    assert user_nodes[0]["fields"]["id"] == DEFAULT_USER_ID
