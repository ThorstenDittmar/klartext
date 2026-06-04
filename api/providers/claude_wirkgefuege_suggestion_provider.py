"""Adapter: suggests a minimal Wirkgefüge from Claims by calling the Claude API."""

from __future__ import annotations

import json
from typing import Any

import anthropic

from api.exceptions.narrative import WirkgefuegeSuggestionError
from api.models.causal_model import EpistemicStatus, SlotType
from api.models.claim import Claim
from api.providers.wirkgefuege_suggestion_provider import (
    SuggestedRelation,
    SuggestedSlot,
    WirkgefuegeSuggestionProvider,
    WirkgefuegeSuggestionResult,
)

_SLOT_TYPES = " | ".join(t.value for t in SlotType)
_EPISTEMIC_STATUSES = " | ".join(t.value for t in EpistemicStatus)

_SYSTEM_PROMPT = f"""Du bist ein Experte für kausale Modellierung.

Gegeben eine Liste von Claims, erstelle ein minimales Wirkgefüge.

Antworte ausschließlich mit einem JSON-Objekt:

"suggested_slots": Array von Objekten mit:
- "identifier": Englischer snake_case-Bezeichner (z.B. "co2_emissions")
- "slot_type": Einer von: {_SLOT_TYPES}

"suggested_relations": Array von Objekten mit:
- "source": Quell-Slot Bezeichner (muss in suggested_slots vorkommen)
- "target": Ziel-Slot Bezeichner (muss in suggested_slots vorkommen)
- "source_condition": Zustandsbeschreibung des Quell-Slots (optional, null)
- "target_effect": Effekt auf den Ziel-Slot (optional, null)
- "mechanism": Kausaler Mechanismus (optional, null)
- "epistemic_status": Einer von: {_EPISTEMIC_STATUSES}

"from_claims": Array der Claim-IDs die zu den Vorschlägen beigetragen haben

Minimale Repräsentation — nur die wichtigsten Slots und Relationen.
Jeder Slot in suggested_relations muss in suggested_slots definiert sein."""


class ClaudeWirkgefuegeSuggestionProvider(WirkgefuegeSuggestionProvider):
    """Calls the Claude API to suggest a minimal Wirkgefüge from a list of Claims.

    The Anthropic client is injected via the constructor so that tests can
    supply a mock without patching module-level imports.
    """

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    async def suggest(self, claims: list[Claim]) -> WirkgefuegeSuggestionResult:
        """Sends the claims to Claude and returns a suggested Wirkgefüge."""
        claims_text = self._format_claims(claims)

        message = await self._client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Schlage ein Wirkgefüge für folgende Claims vor:\n\n{claims_text}",
                }
            ],
        )

        first_block = message.content[0]
        if not isinstance(first_block, anthropic.types.TextBlock):
            raise WirkgefuegeSuggestionError(
                f"Unexpected content block type from Claude API: {type(first_block)}"
            )

        raw = self._strip_code_fences(first_block.text.strip())

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise WirkgefuegeSuggestionError(f"Claude API returned invalid JSON: {e}") from e

        if not isinstance(parsed, dict):
            raise WirkgefuegeSuggestionError(f"Claude API returned unexpected type: {type(parsed)}")

        return WirkgefuegeSuggestionResult(
            suggested_slots=[self._parse_slot(s) for s in parsed.get("suggested_slots", [])],
            suggested_relations=[
                self._parse_relation(r) for r in parsed.get("suggested_relations", [])
            ],
            from_claims=parsed.get("from_claims", [c.id for c in claims if c.id]),
        )

    def _format_claims(self, claims: list[Claim]) -> str:
        """Formats claims as a numbered list with ID, label, text and type."""
        lines = []
        for i, claim in enumerate(claims, 1):
            lines.append(
                f"{i}. ID: {claim.id}\n"
                f"   Label: {claim.label}\n"
                f"   Text: {claim.text}\n"
                f"   Type: {claim.typ.value}"
            )
        return "\n\n".join(lines)

    def _strip_code_fences(self, text: str) -> str:
        """Removes markdown code fences that Claude sometimes wraps its response in."""
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return text.strip()

    def _parse_slot(self, record: dict[str, Any]) -> SuggestedSlot:
        """Converts a raw slot record to a SuggestedSlot.

        Falls back to 'entity_state' for unrecognised slot_type values.
        """
        try:
            SlotType(record.get("slot_type", ""))
            slot_type = record["slot_type"]
        except ValueError:
            slot_type = "entity_state"
        return SuggestedSlot(
            identifier=record.get("identifier", "unknown"),
            slot_type=slot_type,
        )

    def _parse_relation(self, record: dict[str, Any]) -> SuggestedRelation:
        """Converts a raw relation record to a SuggestedRelation.

        Falls back to 'incomplete' for unrecognised epistemic_status values.
        """
        try:
            EpistemicStatus(record.get("epistemic_status", ""))
            epistemic_status = record["epistemic_status"]
        except ValueError:
            epistemic_status = "incomplete"
        return SuggestedRelation(
            source=record.get("source", ""),
            target=record.get("target", ""),
            source_condition=record.get("source_condition"),
            target_effect=record.get("target_effect"),
            mechanism=record.get("mechanism"),
            epistemic_status=epistemic_status,
        )
