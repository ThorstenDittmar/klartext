"""Adapter: extracts Claims from a Scene by calling the Claude API."""

from __future__ import annotations

import json
from typing import Any

import anthropic

from api.exceptions.claim import ClaimExtractionError
from api.models.claim import Claim, ClaimType
from api.models.narrative import Scene
from api.providers.claim_extraction_provider import ClaimExtractionProvider

_CLAIM_TYPES = " | ".join(t.value for t in ClaimType)

_SYSTEM_PROMPT = f"""Du bist ein Experte für epistemische Analyse narrativer Texte.

Deine Aufgabe: Extrahiere vorläufige Claims aus dem gegebenen Text.
Ein Claim ist eine behauptete Aussage –
empirisch, kausal, normativ, prognostisch oder definitorisch.

Antworte ausschließlich mit einem JSON-Array. Jeder Eintrag hat:
- "text": Die extrahierte Aussage (vollständiger Satz, max. 200 Zeichen)
- "typ": Einer von: {_CLAIM_TYPES}
- "confidence": Float zwischen 0.0 und 1.0

Extrahiere nur Claims die explizit oder klar implizit im Text vorhanden sind.
Maximal 10 Claims pro Text. Claims sind vorläufig – nicht verbindlich."""


class ClaudeClaimExtractionProvider(ClaimExtractionProvider):
    """Calls the Claude API to extract Claims from a Scene.

    The Anthropic client is injected via the constructor so that tests can
    supply a mock without patching module-level imports.
    """

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    async def extract(self, scene: Scene) -> list[Claim]:
        """Sends the scene text to Claude and returns the parsed Claims."""
        message = await self._client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Extrahiere Claims aus folgendem Text:\n\n{scene.text}",
                }
            ],
        )

        first_block = message.content[0]
        if not isinstance(first_block, anthropic.types.TextBlock):
            raise ClaimExtractionError(
                f"Unexpected content block type from Claude API: {type(first_block)}"
            )

        raw = self._strip_code_fences(first_block.text.strip())

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ClaimExtractionError(f"Claude API returned invalid JSON: {e}") from e

        if not isinstance(parsed, list):
            raise ClaimExtractionError(
                f"Claude API returned a JSON object instead of an array: {type(parsed)}"
            )

        raw_records: list[dict[str, Any]] = parsed
        return [self._parse_claim(record) for record in raw_records]

    def _strip_code_fences(self, text: str) -> str:
        """Removes markdown code fences that Claude sometimes wraps its response in."""
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return text.strip()

    def _parse_claim(self, record: dict[str, Any]) -> Claim:
        """Converts a raw API record into a Claim, clamping confidence to 0.0–1.0.

        Raises ClaimExtractionError if the API returned an unrecognised claim type.
        """
        try:
            typ = ClaimType(record["typ"])
        except ValueError as e:
            raise ClaimExtractionError(
                f"Claude API returned unknown claim type: {record['typ']}"
            ) from e
        confidence = max(0.0, min(1.0, float(record.get("confidence", 0.5))))
        return Claim.create(text=record["text"], typ=typ, confidence=confidence)
