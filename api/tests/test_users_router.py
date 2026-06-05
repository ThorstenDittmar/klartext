"""Tests for the users router."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_user_service
from api.main import app
from api.services.user_service import UserService
from api.tests.fakes.fake_user_repository import FakeUserRepository


def make_user_service() -> UserService:
    """Returns a UserService backed by the in-memory FakeUserRepository."""
    return UserService(FakeUserRepository())


@pytest.fixture(autouse=True)
def override_user_service():
    """Replaces the real UserService with a fake for every test in this module."""
    app.dependency_overrides[get_user_service] = make_user_service
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_users_health() -> None:
    """Expects GET /users/health to return HTTP 200 with status ok."""
    response = client.get("/users/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
