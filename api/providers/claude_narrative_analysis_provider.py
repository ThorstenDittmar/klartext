"""Adapter: analyses a Narrative by calling the Claude API."""

from __future__ import annotations

import json
from typing import Any

import anthropic

from api.exceptions.narrative import NarrativeAnalysisError
from api.models.claim import ClaimType
from api.models.narrative import ActorType, Narrative
from api.providers.narrative_analysis_provider import (
    ActorOccurrence,
    ActorSuggestion,
    ClaimSuggestion,
    NarrativeAnalysisProvider,
    NarrativeAnalysisResult,
    WirkgefuegeSuggestion,
)

_ACTOR_TYPES = " | ".join(t.value for t in ActorType)
_CLAIM_TYPES = " | ".join(t.value for t in ClaimType)

_SYSTEM_PROMPT = (
    "Du bist ein Experte für die strukturierte Analyse"
    " politischer und wissenschaftlicher Narrative.\n\n"
    "Deine Aufgabe: Analysiere den vollständigen Narrativ-Text"
    " und extrahiere Akteure und Claims.\n\n"
    "Antworte ausschließlich mit einem JSON-Objekt mit zwei Feldern:\n\n"
    '"actors": Array von Objekten mit:\n'
    '- "label": Name oder Bezeichnung des Akteurs\n'
    f'- "actor_type": Einer von: {_ACTOR_TYPES}\n'
    '- "occurrences": Array von Objekten für JEDE Nennung im Text'
    " — direkte Namen UND Pronomen, ALLE Vorkommen:\n"
    '    { "scene_title": "<Szenenname>", "start_offset": <int>, "end_offset": <int> }\n'
    "  start_offset und end_offset sind 0-indexierte Zeichenpositionen relativ zum Szenentext.\n"
    "  end_offset ist exklusiv (erstes Zeichen nach dem Match).\n"
    "  Für implizite Gruppen ohne direkte Textstelle: occurrences = []\n"
    '- "entity_suggestion": Englischer snake_case-Bezeichner für ein'
    ' Kausalmodell-Element (z.B. "central_bank"), null falls unbekannt\n\n'
    "AKTEURSERKENNUNG — vier Kategorien:\n"
    "1. Benannte Einzelpersonen (actor_type='individual'):"
    " namentlich genannte Personen, z.B. 'Maria Müller', 'der Minister'\n"
    "2. Benannte Gruppen (actor_type='group'):"
    " explizit im Text genannte Kollektive, z.B. 'die Bevölkerung',"
    " 'Klimaaktivisten', 'die Demonstranten', 'Verbraucher'\n"
    "3. Benannte Institutionen/Organisationen (actor_type='institution'):"
    " 'die Regierung', 'das Parlament', 'die EZB', 'das Bundesministerium',"
    " Firmen, Behörden, Parteien — auch wenn sie als 'sie/er/es' weiterreferenziert werden\n"
    "4. Implizite Akteure (actor_type='group' oder 'abstract_entity'):"
    " aus dem Kontext erschlossene Gruppen ohne direkten Textbezug — occurrences = []\n\n"
    "PRONOMENERKENNUNG — PFLICHT:\n"
    "Wenn ein Akteur im weiteren Text durch ein Pronomen referenziert wird"
    " (er/sie/es/du/ihr/wir/man/ihm/ihr/ihn/uns/euch/deren/dessen),"
    " füge diese Pronomen-Stellen EBENFALLS zur occurrences-Liste des Akteurs hinzu.\n"
    "start_offset/end_offset zeigen dabei auf das Pronomen selbst im Szenentext.\n"
    "Beispiel: 'Die Regierung beschloss...' → occurrence bei 'Die Regierung'\n"
    "          '...dann verkündete sie den Beschluss...' → WEITERE occurrence bei 'sie'\n\n"
    '"claims": Array von Objekten mit:\n'
    '- "label": Kurzer englischer Titel (max. 80 Zeichen)\n'
    '- "text": Die extrahierte Aussage als wörtliches Zitat'
    " oder enger Paraphrase (max. 200 Zeichen)\n"
    f'- "claim_type": Einer von: {_CLAIM_TYPES}\n'
    '- "confidence": Float zwischen 0.0 und 1.0\n'
    '- "scene_title": Titel der Szene aus der der Claim stammt\n'
    '- "start_offset": Zeichenposition im Szenentext wo die Aussage beginnt (0-indexiert)\n'
    '- "end_offset": Zeichenposition im Szenentext wo die Aussage endet (exklusiv)\n'
    '- "wirkgefuege_suggestion": null oder Objekt mit:\n'
    '  - "type": "slot_state" oder "causal_relation"\n'
    '  - Für "slot_state": "slot" (snake_case, englisch), "slot_state" (Zustandsbeschreibung)\n'
    '  - Für "causal_relation": "source_slot", "source_condition", "target_slot",'
    ' "target_effect", "mechanism" (alles snake_case/englisch)\n\n'
    "Maximal 8 Akteure und 10 Claims."
    " Nur was explizit oder klar implizit im Text vorhanden ist."
)


class ClaudeNarrativeAnalysisProvider(NarrativeAnalysisProvider):
    """Calls the Claude API to analyse a Narrative and return actor and claim suggestions.

    The Anthropic client is injected via the constructor so that tests can
    supply a mock without patching module-level imports.
    """

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    async def analyse(self, narrative: Narrative) -> NarrativeAnalysisResult:
        """Sends all scene texts to Claude and returns parsed actor and claim suggestions."""
        narrative_text = self._format_narrative(narrative)

        message = await self._client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8192,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Analysiere folgenden Narrativ:\n\n{narrative_text}",
                }
            ],
        )

        first_block = message.content[0]
        if not isinstance(first_block, anthropic.types.TextBlock):
            raise NarrativeAnalysisError(
                f"Unexpected content block type from Claude API: {type(first_block)}"
            )

        raw = self._strip_code_fences(first_block.text.strip())

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise NarrativeAnalysisError(f"Claude API returned invalid JSON: {e}") from e

        if not isinstance(parsed, dict):
            raise NarrativeAnalysisError(f"Claude API returned unexpected type: {type(parsed)}")

        return NarrativeAnalysisResult(
            actors=[self._parse_actor(a) for a in parsed.get("actors", [])],
            claims=[self._parse_claim(c) for c in parsed.get("claims", [])],
        )

    def _format_narrative(self, narrative: Narrative) -> str:
        """Formats all scenes into a single text block with scene headers.

        Offsets returned by the LLM are relative to the scene text (the content
        after the ## header), not the full formatted output.
        """
        parts = [f"# {narrative.title}"]
        for scene in narrative.scenes:
            parts.append(f"\n## {scene.title}\n\n{scene.text}")
        return "\n".join(parts)

    def _strip_code_fences(self, text: str) -> str:
        """Removes markdown code fences that Claude sometimes wraps its response in."""
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return text.strip()

    def _parse_actor(self, record: dict[str, Any]) -> ActorSuggestion:
        """Converts a raw actor record to an ActorSuggestion.

        Falls back to 'abstract_entity' for unrecognised actor_type values.
        Parses all occurrences with their character offsets.
        """
        try:
            ActorType(record.get("actor_type", ""))
            actor_type = record["actor_type"]
        except ValueError:
            actor_type = "abstract_entity"

        occurrences = [
            ActorOccurrence(
                scene_title=occ.get("scene_title", ""),
                start_offset=occ.get("start_offset"),
                end_offset=occ.get("end_offset"),
            )
            for occ in record.get("occurrences", [])
            if isinstance(occ, dict)
        ]

        return ActorSuggestion(
            label=record.get("label", "Unknown"),
            actor_type=actor_type,
            occurrences=occurrences,
            entity_suggestion=record.get("entity_suggestion"),
        )

    def _parse_claim(self, record: dict[str, Any]) -> ClaimSuggestion:
        """Converts a raw claim record to a ClaimSuggestion.

        Falls back to 'empirical' for unrecognised claim_type values.
        Clamps confidence to 0.0–1.0. Captures scene offsets when present.
        """
        try:
            ClaimType(record.get("claim_type", ""))
            claim_type = record["claim_type"]
        except ValueError:
            claim_type = "empirical"

        confidence = max(0.0, min(1.0, float(record.get("confidence", 0.5))))

        raw_ws = record.get("wirkgefuege_suggestion")
        wirkgefuege_suggestion = self._parse_wirkgefuege_suggestion(raw_ws) if raw_ws else None

        return ClaimSuggestion(
            label=record.get("label") or record.get("text", "")[:80],
            text=record.get("text", ""),
            claim_type=claim_type,
            confidence=confidence,
            wirkgefuege_suggestion=wirkgefuege_suggestion,
            scene_title=record.get("scene_title"),
            start_offset=record.get("start_offset"),
            end_offset=record.get("end_offset"),
        )

    def _parse_wirkgefuege_suggestion(self, record: dict[str, Any]) -> WirkgefuegeSuggestion:
        """Converts a raw wirkgefuege_suggestion record to a WirkgefuegeSuggestion.

        Raises NarrativeAnalysisError if the record is not a JSON object.
        """
        if not isinstance(record, dict):
            raise NarrativeAnalysisError(
                f"wirkgefuege_suggestion must be a JSON object, got: {type(record)}"
            )
        return WirkgefuegeSuggestion(
            suggestion_type=record.get("type", "slot_state"),
            slot=record.get("slot"),
            slot_state=record.get("slot_state"),
            source_slot=record.get("source_slot"),
            source_condition=record.get("source_condition"),
            target_slot=record.get("target_slot"),
            target_effect=record.get("target_effect"),
            mechanism=record.get("mechanism"),
        )
