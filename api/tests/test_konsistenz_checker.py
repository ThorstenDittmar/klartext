"""Tests for the KonsistenzChecker port and ClaudeKonsistenzChecker adapter.

Unit tests use a FakeKonsistenzChecker for deterministic behaviour.
The integration test calls the real Claude API.
"""

from __future__ import annotations

import pytest

from api.models.wirkmodell import Axiom
from api.providers.konsistenz_checker import (
    KonsistenzChecker,
    KonsistenzKonflikt,
    KonsistenzResult,
)
from tests.mothers.wirkmodell_mother import AxiomMother


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class AlwaysKonsistentChecker(KonsistenzChecker):
    """Returns consistent for any input."""

    async def check(self, szenen_text: str, axiome: list[Axiom]) -> KonsistenzResult:
        return KonsistenzResult(konsistent=True)


class AlwaysKonfliktChecker(KonsistenzChecker):
    """Returns one conflict for every Axiom passed in."""

    async def check(self, szenen_text: str, axiome: list[Axiom]) -> KonsistenzResult:
        konflikte = [
            KonsistenzKonflikt(
                axiom_label=a.label,
                beschreibung=f"Konflikt mit {a.label}",
                vorschlag="Szene anpassen oder Axiom erweitern.",
            )
            for a in axiome
        ]
        return KonsistenzResult(konsistent=False, konflikte=konflikte)


# ---------------------------------------------------------------------------
# Unit tests — port contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_konsistent_result_has_no_konflikte() -> None:
    """Expects a consistent result to have an empty konflikte list."""
    checker = AlwaysKonsistentChecker()

    result = await checker.check("Eine Szene.", AxiomMother.collection())

    assert result.konsistent is True
    assert result.konflikte == []


@pytest.mark.asyncio
async def test_konflikt_result_is_not_konsistent() -> None:
    """Expects a result with konflikte to have konsistent=False."""
    checker = AlwaysKonfliktChecker()

    result = await checker.check("Eine Szene.", AxiomMother.collection())

    assert result.konsistent is False


@pytest.mark.asyncio
async def test_konflikt_result_contains_one_entry_per_axiom() -> None:
    """Expects one KonsistenzKonflikt per Axiom when all conflict."""
    checker = AlwaysKonfliktChecker()
    axiome = AxiomMother.collection()

    result = await checker.check("Eine Szene.", axiome)

    assert len(result.konflikte) == len(axiome)


@pytest.mark.asyncio
async def test_konflikt_entry_contains_axiom_label() -> None:
    """Expects each KonsistenzKonflikt to reference its Axiom by label."""
    checker = AlwaysKonfliktChecker()

    result = await checker.check("Eine Szene.", [AxiomMother.zins()])

    assert result.konflikte[0].axiom_label == "A-01"


@pytest.mark.asyncio
async def test_checker_with_empty_axiome_list_returns_consistent() -> None:
    """Expects a consistent result when no Axiome are provided."""
    checker = AlwaysKonsistentChecker()

    result = await checker.check("Eine Szene.", axiome=[])

    assert result.konsistent is True


# ---------------------------------------------------------------------------
# ClaudeKonsistenzChecker unit tests (mocked API)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_claude_checker_returns_konsistent_result_for_consistent_scene() -> None:
    """Expects ClaudeKonsistenzChecker to return konsistent=True for a mock consistent response."""
    import json
    from unittest.mock import AsyncMock, MagicMock

    import anthropic

    from api.providers.claude_konsistenz_checker import ClaudeKonsistenzChecker

    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(text=json.dumps({"konsistent": True, "konflikte": []}))
    ]

    mock_client = MagicMock(spec=anthropic.AsyncAnthropic)
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    checker = ClaudeKonsistenzChecker(client=mock_client)

    result = await checker.check("Eine konsistente Szene.", [AxiomMother.zins()])

    assert result.konsistent is True
    assert result.konflikte == []


@pytest.mark.asyncio
async def test_claude_checker_returns_konflikt_for_conflicting_scene() -> None:
    """Expects ClaudeKonsistenzChecker to parse konflikte from the API response."""
    import json
    from unittest.mock import AsyncMock, MagicMock

    import anthropic

    from api.providers.claude_konsistenz_checker import ClaudeKonsistenzChecker

    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(text=json.dumps({
            "konsistent": False,
            "konflikte": [
                {
                    "axiom_label": "A-01",
                    "beschreibung": "Die Szene beschreibt steigende Investitionen nach Zinserhöhung.",
                    "vorschlag": "Ausnahmebedingung ergänzen oder Axiom A-01 erweitern.",
                }
            ],
        }))
    ]

    mock_client = MagicMock(spec=anthropic.AsyncAnthropic)
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    checker = ClaudeKonsistenzChecker(client=mock_client)

    result = await checker.check("Unternehmen investieren massiv.", [AxiomMother.zins()])

    assert result.konsistent is False
    assert len(result.konflikte) == 1
    assert result.konflikte[0].axiom_label == "A-01"
    assert result.konflikte[0].vorschlag is not None


# ---------------------------------------------------------------------------
# Integration — real Claude API
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_claude_checker_detects_conflict_with_real_api() -> None:
    """Calls the real Claude API. Expects a conflict for a scene that contradicts A-01.

    Requires ANTHROPIC_API_KEY to be set.
    """
    import os

    import anthropic

    from api.providers.claude_konsistenz_checker import ClaudeKonsistenzChecker

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    checker = ClaudeKonsistenzChecker(client=client)

    conflicting_scene = (
        "Unmittelbar nach der drastischen Zinserhöhung der Zentralbank "
        "verzeichneten alle großen Unternehmen massive Investitionssteigerungen, "
        "ohne dass äußere Faktoren dies erklärten."
    )

    result = await checker.check(conflicting_scene, [AxiomMother.zins()])

    assert isinstance(result, KonsistenzResult)
    assert result.konsistent is False
    assert len(result.konflikte) > 0
