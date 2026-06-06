"""Unit tests for ClaudeNarrativeAnalysisProvider parsing methods.

Tests _parse_actor and _parse_claim directly with crafted JSON records.
No API calls — the anthropic client is not used by these methods.
"""

from __future__ import annotations

import pytest

from api.providers.claude_narrative_analysis_provider import ClaudeNarrativeAnalysisProvider
from api.providers.narrative_analysis_provider import ActorOccurrence

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_provider() -> ClaudeNarrativeAnalysisProvider:
    """Creates a provider instance without a real API client.

    The parsing methods do not touch self._client, so None is safe here.
    """
    return ClaudeNarrativeAnalysisProvider(client=None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _parse_actor
# ---------------------------------------------------------------------------


def test_parse_actor_standard_occurrence() -> None:
    """Expects a single ActorOccurrence with scene_title and integer offsets."""
    provider = make_provider()
    record = {
        "label": "EZB",
        "actor_type": "institution",
        "occurrences": [
            {"scene_title": "Szene 1", "start_offset": 4, "end_offset": 7},
        ],
        "entity_suggestion": "ecb",
    }

    actor = provider._parse_actor(record)

    assert actor.label == "EZB"
    assert actor.actor_type == "institution"
    assert len(actor.occurrences) == 1
    assert actor.occurrences[0].scene_title == "Szene 1"
    assert actor.occurrences[0].start_offset == 4
    assert actor.occurrences[0].end_offset == 7


def test_parse_actor_multiple_occurrences() -> None:
    """Expects all occurrences to be parsed when the LLM returns more than one."""
    provider = make_provider()
    record = {
        "label": "Minister",
        "actor_type": "individual",
        "occurrences": [
            {"scene_title": "Szene 1", "start_offset": 0, "end_offset": 8},
            {"scene_title": "Szene 2", "start_offset": 12, "end_offset": 20},
        ],
        "entity_suggestion": None,
    }

    actor = provider._parse_actor(record)

    assert len(actor.occurrences) == 2
    assert actor.occurrences[0].scene_title == "Szene 1"
    assert actor.occurrences[1].scene_title == "Szene 2"


def test_parse_actor_empty_occurrences_for_implicit_group() -> None:
    """Expects an empty occurrences list when actor_type is group with no text reference."""
    provider = make_provider()
    record = {
        "label": "Klimaaktivisten",
        "actor_type": "group",
        "occurrences": [],
        "entity_suggestion": None,
    }

    actor = provider._parse_actor(record)

    assert actor.actor_type == "group"
    assert actor.occurrences == []


def test_parse_actor_missing_occurrences_key() -> None:
    """Expects an empty occurrences list when the LLM omits the occurrences key entirely."""
    provider = make_provider()
    record = {
        "label": "Behörde",
        "actor_type": "institution",
        "entity_suggestion": None,
    }

    actor = provider._parse_actor(record)

    assert actor.occurrences == []


def test_parse_actor_null_offsets_in_occurrence() -> None:
    """Expects start_offset and end_offset to be None when the LLM returns null."""
    provider = make_provider()
    record = {
        "label": "Gruppe",
        "actor_type": "group",
        "occurrences": [
            {"scene_title": "Szene 1", "start_offset": None, "end_offset": None},
        ],
        "entity_suggestion": None,
    }

    actor = provider._parse_actor(record)

    occ = actor.occurrences[0]
    assert isinstance(occ, ActorOccurrence)
    assert occ.scene_title == "Szene 1"
    assert occ.start_offset is None
    assert occ.end_offset is None


def test_parse_actor_skips_non_dict_occurrence_entries() -> None:
    """Expects non-dict entries in occurrences (e.g. stray strings) to be silently ignored."""
    provider = make_provider()
    record = {
        "label": "Akteur",
        "actor_type": "individual",
        "occurrences": [
            "not-a-dict",
            {"scene_title": "Szene 1", "start_offset": 0, "end_offset": 5},
        ],
        "entity_suggestion": None,
    }

    actor = provider._parse_actor(record)

    assert len(actor.occurrences) == 1
    assert actor.occurrences[0].scene_title == "Szene 1"


def test_parse_actor_falls_back_to_abstract_entity_for_unknown_type() -> None:
    """Expects actor_type to fall back to 'abstract_entity' for unrecognised values."""
    provider = make_provider()
    record = {
        "label": "Unbekannt",
        "actor_type": "alien_species",
        "occurrences": [],
        "entity_suggestion": None,
    }

    actor = provider._parse_actor(record)

    assert actor.actor_type == "abstract_entity"


def test_parse_actor_uses_unknown_label_as_fallback() -> None:
    """Expects label to fall back to 'Unknown' when missing from the record."""
    provider = make_provider()
    record = {"actor_type": "individual", "occurrences": [], "entity_suggestion": None}

    actor = provider._parse_actor(record)

    assert actor.label == "Unknown"


# ---------------------------------------------------------------------------
# _parse_claim
# ---------------------------------------------------------------------------


def test_parse_claim_standard_fields() -> None:
    """Expects all fields to be parsed correctly from a full claim record."""
    provider = make_provider()
    record = {
        "label": "Inflation rises with money supply",
        "text": "Higher money supply leads to inflation.",
        "claim_type": "causal",
        "confidence": 0.9,
        "wirkgefuege_suggestion": None,
        "scene_title": "Szene 1",
        "start_offset": 10,
        "end_offset": 50,
    }

    claim = provider._parse_claim(record)

    assert claim.label == "Inflation rises with money supply"
    assert claim.claim_type == "causal"
    assert claim.confidence == pytest.approx(0.9)
    assert claim.scene_title == "Szene 1"
    assert claim.start_offset == 10
    assert claim.end_offset == 50


def test_parse_claim_null_offsets() -> None:
    """Expects scene_title, start_offset and end_offset to be None when the LLM returns null."""
    provider = make_provider()
    record = {
        "label": "Some claim",
        "text": "A statement.",
        "claim_type": "empirical",
        "confidence": 0.7,
        "wirkgefuege_suggestion": None,
        "scene_title": None,
        "start_offset": None,
        "end_offset": None,
    }

    claim = provider._parse_claim(record)

    assert claim.scene_title is None
    assert claim.start_offset is None
    assert claim.end_offset is None


def test_parse_claim_missing_offset_keys() -> None:
    """Expects scene_title, start_offset and end_offset to be None when keys are absent."""
    provider = make_provider()
    record = {
        "label": "Some claim",
        "text": "A statement.",
        "claim_type": "empirical",
        "confidence": 0.5,
        "wirkgefuege_suggestion": None,
    }

    claim = provider._parse_claim(record)

    assert claim.scene_title is None
    assert claim.start_offset is None
    assert claim.end_offset is None


def test_parse_claim_falls_back_to_empirical_for_unknown_type() -> None:
    """Expects claim_type to fall back to 'empirical' for unrecognised values."""
    provider = make_provider()
    record = {
        "label": "Odd claim",
        "text": "Something odd.",
        "claim_type": "metaphysical",
        "confidence": 0.5,
        "wirkgefuege_suggestion": None,
    }

    claim = provider._parse_claim(record)

    assert claim.claim_type == "empirical"


def test_parse_claim_clamps_confidence_above_one() -> None:
    """Expects confidence to be clamped to 1.0 when the LLM returns a value above 1."""
    provider = make_provider()
    record = {
        "label": "Claim",
        "text": "Text.",
        "claim_type": "empirical",
        "confidence": 1.5,
        "wirkgefuege_suggestion": None,
    }

    claim = provider._parse_claim(record)

    assert claim.confidence == pytest.approx(1.0)


def test_parse_claim_clamps_confidence_below_zero() -> None:
    """Expects confidence to be clamped to 0.0 when the LLM returns a negative value."""
    provider = make_provider()
    record = {
        "label": "Claim",
        "text": "Text.",
        "claim_type": "empirical",
        "confidence": -0.3,
        "wirkgefuege_suggestion": None,
    }

    claim = provider._parse_claim(record)

    assert claim.confidence == pytest.approx(0.0)


def test_parse_actor_named_institution_with_direct_text_occurrence() -> None:
    """Expects a named institution ('die Regierung') to be parsed with actor_type 'institution'.

    Verifies that its direct text occurrence is correctly extracted from the record.
    """
    provider = make_provider()
    record = {
        "label": "Die Regierung",
        "actor_type": "institution",
        "occurrences": [
            {"scene_title": "Einleitung", "start_offset": 0, "end_offset": 13},
        ],
        "entity_suggestion": "government",
    }

    actor = provider._parse_actor(record)

    assert actor.label == "Die Regierung"
    assert actor.actor_type == "institution"
    assert len(actor.occurrences) == 1
    assert actor.occurrences[0].scene_title == "Einleitung"
    assert actor.occurrences[0].start_offset == 0
    assert actor.occurrences[0].end_offset == 13
    assert actor.entity_suggestion == "government"


def test_parse_actor_pronoun_occurrences_are_included_as_regular_occurrences() -> None:
    """Expects pronoun references ('sie', 'er') to appear as regular occurrences.

    They should appear alongside the direct name reference of the same actor.
    """
    provider = make_provider()
    record = {
        "label": "Die Regierung",
        "actor_type": "institution",
        "occurrences": [
            # Direct name reference
            {"scene_title": "Szene 1", "start_offset": 0, "end_offset": 13},
            # Pronoun "sie" referring back to "Die Regierung"
            {"scene_title": "Szene 1", "start_offset": 42, "end_offset": 45},
            # Pronoun "sie" in a different scene
            {"scene_title": "Szene 2", "start_offset": 8, "end_offset": 11},
        ],
        "entity_suggestion": "government",
    }

    actor = provider._parse_actor(record)

    assert len(actor.occurrences) == 3
    assert actor.occurrences[0].start_offset == 0  # direct name
    assert actor.occurrences[1].start_offset == 42  # pronoun in scene 1
    assert actor.occurrences[2].start_offset == 8  # pronoun in scene 2
    assert actor.occurrences[2].scene_title == "Szene 2"


def test_parse_claim_uses_text_as_label_fallback() -> None:
    """Expects label to be truncated text when label is missing or empty."""
    provider = make_provider()
    long_text = "A" * 100
    record = {
        "label": "",
        "text": long_text,
        "claim_type": "empirical",
        "confidence": 0.5,
        "wirkgefuege_suggestion": None,
    }

    claim = provider._parse_claim(record)

    assert len(claim.label) == 80
    assert claim.label == "A" * 80
