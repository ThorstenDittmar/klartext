"""Tests for the /health endpoint.

The health check must report API status and each infrastructure dependency
(database, anthropic) independently. It returns 200 even when dependencies
are degraded — the caller reads the individual check results.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.dependencies import get_health_checker
from api.main import app
from api.services.health_service import HealthChecker, HealthResult, HealthStatus

# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class AlwaysOkHealthChecker(HealthChecker):
    """Fake that reports all dependencies as healthy."""

    async def check_database(self) -> HealthResult:
        """Returns a healthy database result."""
        return HealthResult(name="database", status=HealthStatus.OK)

    async def check_anthropic(self) -> HealthResult:
        """Returns a healthy Anthropic result."""
        return HealthResult(name="anthropic", status=HealthStatus.OK)


class DatabaseDownHealthChecker(HealthChecker):
    """Fake that reports the database as unreachable."""

    async def check_database(self) -> HealthResult:
        """Returns a degraded database result."""
        return HealthResult(name="database", status=HealthStatus.ERROR, detail="connection refused")

    async def check_anthropic(self) -> HealthResult:
        """Returns a healthy Anthropic result."""
        return HealthResult(name="anthropic", status=HealthStatus.OK)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_returns_200() -> None:
    """Expects a 200 response regardless of dependency health."""
    app.dependency_overrides[get_health_checker] = lambda: AlwaysOkHealthChecker()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    app.dependency_overrides.clear()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_ok_status_when_all_healthy() -> None:
    """Expects status 'ok' when all dependencies are healthy."""
    app.dependency_overrides[get_health_checker] = lambda: AlwaysOkHealthChecker()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    app.dependency_overrides.clear()
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_includes_version() -> None:
    """Expects a version field in the response."""
    app.dependency_overrides[get_health_checker] = lambda: AlwaysOkHealthChecker()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    app.dependency_overrides.clear()
    assert "version" in response.json()


@pytest.mark.asyncio
async def test_health_includes_checks_object() -> None:
    """Expects a 'checks' object with per-dependency results."""
    app.dependency_overrides[get_health_checker] = lambda: AlwaysOkHealthChecker()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    app.dependency_overrides.clear()
    body = response.json()
    assert "checks" in body
    assert "database" in body["checks"]
    assert "anthropic" in body["checks"]


@pytest.mark.asyncio
async def test_health_returns_degraded_status_when_database_is_down() -> None:
    """Expects status 'degraded' when the database is unreachable."""
    app.dependency_overrides[get_health_checker] = lambda: DatabaseDownHealthChecker()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    app.dependency_overrides.clear()
    assert response.json()["status"] == "degraded"


@pytest.mark.asyncio
async def test_health_returns_200_even_when_database_is_down() -> None:
    """Expects 200 even when a dependency is down — caller reads check details."""
    app.dependency_overrides[get_health_checker] = lambda: DatabaseDownHealthChecker()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    app.dependency_overrides.clear()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_includes_error_detail_for_failed_check() -> None:
    """Expects the check entry to include an error detail when a dependency fails."""
    app.dependency_overrides[get_health_checker] = lambda: DatabaseDownHealthChecker()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    app.dependency_overrides.clear()
    checks = response.json()["checks"]
    assert checks["database"]["status"] == "error"
    assert "detail" in checks["database"]
