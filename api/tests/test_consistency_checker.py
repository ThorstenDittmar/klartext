"""Tests for the ConsistencyChecker port and ClaudeConsistencyChecker adapter.

Unit tests use FakeConsistencyChecker implementations for deterministic behaviour.
The integration test calls the real Claude API.
"""

from __future__ import annotations

import anthropic
import pytest

from api.models.causal_model import Axiom
from api.providers.consistency_checker import (
    ConsistencyChecker,
    ConsistencyConflict,
    ConsistencyResult,
)
from tests.mothers.causal_model_mother import AxiomMother

# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class AlwaysConsistentChecker(ConsistencyChecker):
    """Returns consistent for any input."""

    async def check(self, scene_text: str, axioms: list[Axiom]) -> ConsistencyResult:
        return ConsistencyResult(consistent=True)


class AlwaysConflictChecker(ConsistencyChecker):
    """Returns one conflict for every Axiom passed in."""

    async def check(self, scene_text: str, axioms: list[Axiom]) -> ConsistencyResult:
        conflicts = [
            ConsistencyConflict(
                axiom_label=a.label,
                description=f"Konflikt mit {a.label}",
                suggestion="Szene anpassen oder Axiom erweitern.",
            )
            for a in axioms
        ]
        return ConsistencyResult(consistent=False, conflicts=conflicts)


# ---------------------------------------------------------------------------
# Unit tests — port contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_consistent_result_has_no_conflicts() -> None:
    """Expects a consistent result to have an empty conflicts list."""
    checker = AlwaysConsistentChecker()

    result = await checker.check("Eine Szene.", AxiomMother.collection())

    assert result.consistent is True
    assert result.conflicts == []


@pytest.mark.asyncio
async def test_conflict_result_is_not_consistent() -> None:
    """Expects a result with conflicts to have consistent=False."""
    checker = AlwaysConflictChecker()

    result = await checker.check("Eine Szene.", AxiomMother.collection())

    assert result.consistent is False


@pytest.mark.asyncio
async def test_conflict_result_contains_one_entry_per_axiom() -> None:
    """Expects one ConsistencyConflict per Axiom when all conflict."""
    checker = AlwaysConflictChecker()
    axioms = AxiomMother.collection()

    result = await checker.check("Eine Szene.", axioms)

    assert len(result.conflicts) == len(axioms)


@pytest.mark.asyncio
async def test_conflict_entry_contains_axiom_label() -> None:
    """Expects each ConsistencyConflict to reference its Axiom by label."""
    checker = AlwaysConflictChecker()

    result = await checker.check("Eine Szene.", [AxiomMother.interest_rate()])

    assert result.conflicts[0].axiom_label == "A-01"


@pytest.mark.asyncio
async def test_checker_with_empty_axioms_list_returns_consistent() -> None:
    """Expects a consistent result when no Axioms are provided."""
    checker = AlwaysConsistentChecker()

    result = await checker.check("Eine Szene.", axioms=[])

    assert result.consistent is True


# ---------------------------------------------------------------------------
# ClaudeConsistencyChecker unit tests (mocked API)
# ---------------------------------------------------------------------------


def _make_text_block(text: str) -> anthropic.types.TextBlock:
    """Creates a real TextBlock so isinstance() checks pass in provider code."""
    return anthropic.types.TextBlock(type="text", text=text)


@pytest.mark.asyncio
async def test_claude_checker_returns_consistent_result_for_consistent_scene() -> None:
    """Expects ClaudeConsistencyChecker to return consistent=True for a mock consistent response."""
    import json
    from unittest.mock import AsyncMock, MagicMock

    from api.providers.claude_consistency_checker import ClaudeConsistencyChecker

    mock_response = MagicMock()
    mock_response.content = [_make_text_block(json.dumps({"consistent": True, "conflicts": []}))]

    mock_client = MagicMock(spec=anthropic.AsyncAnthropic)
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    checker = ClaudeConsistencyChecker(client=mock_client)

    result = await checker.check("Eine konsistente Szene.", [AxiomMother.interest_rate()])

    assert result.consistent is True
    assert result.conflicts == []


@pytest.mark.asyncio
async def test_claude_checker_strips_markdown_code_fences_from_response() -> None:
    """Expects ClaudeConsistencyChecker to handle responses wrapped in markdown code fences."""
    import json
    from unittest.mock import AsyncMock, MagicMock

    from api.providers.claude_consistency_checker import ClaudeConsistencyChecker

    raw_json = json.dumps({"consistent": True, "conflicts": []})
    fenced_response = f"```json\n{raw_json}\n```"

    mock_response = MagicMock()
    mock_response.content = [_make_text_block(fenced_response)]

    mock_client = MagicMock(spec=anthropic.AsyncAnthropic)
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    checker = ClaudeConsistencyChecker(client=mock_client)

    result = await checker.check("Eine Szene.", [AxiomMother.interest_rate()])

    assert result.consistent is True


@pytest.mark.asyncio
async def test_claude_checker_returns_conflict_for_conflicting_scene() -> None:
    """Expects ClaudeConsistencyChecker to parse conflicts from the API response."""
    import json
    from unittest.mock import AsyncMock, MagicMock

    from api.providers.claude_consistency_checker import ClaudeConsistencyChecker

    mock_response = MagicMock()
    mock_response.content = [
        _make_text_block(
            json.dumps(
                {
                    "consistent": False,
                    "conflicts": [
                        {
                            "axiom_label": "A-01",
                            "description": (
                                "Die Szene beschreibt steigende Investitionen nach Zinserhöhung."
                            ),
                            "suggestion": "Ausnahmebedingung ergänzen oder Axiom A-01 erweitern.",
                        }
                    ],
                }
            )
        )
    ]

    mock_client = MagicMock(spec=anthropic.AsyncAnthropic)
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    checker = ClaudeConsistencyChecker(client=mock_client)

    result = await checker.check("Unternehmen investieren massiv.", [AxiomMother.interest_rate()])

    assert result.consistent is False
    assert len(result.conflicts) == 1
    assert result.conflicts[0].axiom_label == "A-01"
    assert result.conflicts[0].suggestion is not None


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

    from api.providers.claude_consistency_checker import ClaudeConsistencyChecker

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    checker = ClaudeConsistencyChecker(client=client)

    conflicting_scene = (
        "Unmittelbar nach der drastischen Zinserhöhung der Zentralbank "
        "verzeichneten alle großen Unternehmen massive Investitionssteigerungen, "
        "ohne dass äußere Faktoren dies erklärten."
    )

    result = await checker.check(conflicting_scene, [AxiomMother.interest_rate()])

    assert isinstance(result, ConsistencyResult)
    assert result.consistent is False
    assert len(result.conflicts) > 0
