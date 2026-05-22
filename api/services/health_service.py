"""Health check service — checks infrastructure dependencies.

Follows the Ports & Adapters pattern: HealthChecker is the port (ABC),
SupabaseHealthChecker is the adapter used in production.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

import anthropic
from supabase import AsyncClient


class HealthStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"  # overall status when one or more checks fail
    ERROR = "error"  # per-check status for failed individual checks


class HealthResult:
    """Holds the result of a single infrastructure check."""

    def __init__(self, name: str, status: HealthStatus, detail: str | None = None) -> None:
        self.name = name
        self.status = status
        self.detail = detail

    def to_dict(self) -> dict[str, str]:
        """Serialises the result to a plain dict for JSON responses."""
        result: dict[str, str] = {"status": self.status.value}
        if self.detail is not None:
            result["detail"] = self.detail
        return result


class HealthChecker(ABC):
    """Port — defines the contract for infrastructure health checks."""

    @abstractmethod
    async def check_database(self) -> HealthResult:
        """Checks whether the Supabase database is reachable."""

    @abstractmethod
    async def check_anthropic(self) -> HealthResult:
        """Checks whether the Anthropic API is reachable."""


class SupabaseHealthChecker(HealthChecker):
    """Adapter — checks real Supabase and Anthropic connectivity."""

    def __init__(self, supabase_client: AsyncClient) -> None:
        self._client = supabase_client

    async def check_database(self) -> HealthResult:
        """Runs a lightweight query against Supabase to confirm the DB is reachable."""
        try:
            await self._client.table("narrative").select("id").limit(1).execute()
            return HealthResult(name="database", status=HealthStatus.OK)
        except Exception as exc:
            return HealthResult(name="database", status=HealthStatus.ERROR, detail=str(exc))

    async def check_anthropic(self) -> HealthResult:
        """Attempts to list models via the Anthropic SDK to confirm the API is reachable."""
        try:
            client = anthropic.AsyncAnthropic()
            await client.models.list()
            return HealthResult(name="anthropic", status=HealthStatus.OK)
        except Exception as exc:
            return HealthResult(name="anthropic", status=HealthStatus.ERROR, detail=str(exc))
