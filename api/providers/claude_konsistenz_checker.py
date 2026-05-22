"""ClaudeKonsistenzChecker — checks scene consistency against Axiome via Claude."""

from __future__ import annotations

import json

import anthropic

from api.models.wirkmodell import Axiom
from api.providers.konsistenz_checker import (
    KonsistenzChecker,
    KonsistenzKonflikt,
    KonsistenzResult,
)

_SYSTEM_PROMPT = """\
Du bist ein Prüfsystem für kausale Konsistenz in Wirkmodellen.

Du erhältst:
1. Eine Szene aus einem Narrativ (Freitext)
2. Eine Liste von Axiomen – axiomat­ischen Annahmen eines formalen Wirkmodells

Deine Aufgabe: Prüfe, ob die Szene mit den Axiomen konsistent ist.

Eine Inkonsistenz liegt vor, wenn die Szene eine Entwicklung beschreibt,
die einem Axiom direkt widerspricht – ohne dass eine Ausnahmebedingung
im Text erklärt wird.

Antworte ausschließlich mit gültigem JSON in diesem Format:
{
  "konsistent": true | false,
  "konflikte": [
    {
      "axiom_label": "A-01",
      "beschreibung": "Kurze Beschreibung warum die Szene mit diesem Axiom konfligiert.",
      "vorschlag": "Optional: Wie könnte Autor oder Axiom angepasst werden?"
    }
  ]
}

Wenn keine Konflikte vorliegen, ist "konflikte" eine leere Liste.
Antworte nur mit dem JSON-Objekt, ohne Erklärungen davor oder danach.\
"""


class ClaudeKonsistenzChecker(KonsistenzChecker):
    """Adapter — uses Claude to check scene text against Wirkmodell axioms."""

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    async def check(self, szenen_text: str, axiome: list[Axiom]) -> KonsistenzResult:
        """Sends the scene and axioms to Claude and parses the consistency verdict."""
        if not axiome:
            return KonsistenzResult(konsistent=True)

        axiom_block = "\n".join(
            f"- {a.label}: {a.beschreibung}" for a in axiome
        )
        user_message = f"Szene:\n{szenen_text}\n\nAxiome:\n{axiom_block}"

        response = await self._client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        data = json.loads(raw)
        konflikte = [
            KonsistenzKonflikt(
                axiom_label=k["axiom_label"],
                beschreibung=k["beschreibung"],
                vorschlag=k.get("vorschlag"),
            )
            for k in data.get("konflikte", [])
        ]
        return KonsistenzResult(konsistent=data["konsistent"], konflikte=konflikte)
