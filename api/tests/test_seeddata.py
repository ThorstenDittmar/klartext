"""Tests for the seed data module.

Verifies that seed data builders produce valid, consistent domain objects.
These tests catch regressions when domain object invariants change.
"""

from __future__ import annotations

from api.models.narrative import Narrative
from api.seeddata import SEED_CLAIMS, build_simple_narrative


def test_build_simple_narrative_returns_narrative() -> None:
    """Expects build_simple_narrative to return a Narrative instance."""
    result = build_simple_narrative()

    assert isinstance(result, Narrative)


def test_build_simple_narrative_has_title() -> None:
    """Expects the seed narrative to have a non-empty title."""
    result = build_simple_narrative()

    assert result.title.strip() != ""


def test_build_simple_narrative_has_three_scenes() -> None:
    """Expects the seed narrative to have exactly three scenes."""
    result = build_simple_narrative()

    assert len(result.scenes) == 3


def test_build_simple_narrative_scenes_have_ascending_positions() -> None:
    """Expects scene positions to start at 1 and increase by 1."""
    result = build_simple_narrative()

    positions = [s.position for s in result.scenes]
    assert positions == [1, 2, 3]


def test_build_simple_narrative_scenes_have_non_empty_text() -> None:
    """Expects every scene to have non-empty title and text."""
    result = build_simple_narrative()

    for scene in result.scenes:
        assert scene.title.strip() != ""
        assert scene.text.strip() != ""


def test_seed_claims_covers_first_three_scenes() -> None:
    """Expects SEED_CLAIMS to contain entries for scene indices 0, 1 and 2."""
    indices = {s.scene_index for s in SEED_CLAIMS}

    assert indices == {0, 1, 2}


