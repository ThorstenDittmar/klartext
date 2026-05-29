"""ClaudeConsistencyChecker — checks scene consistency against Axioms via Claude."""

from __future__ import annotations

import json

import anthropic

from api.models.causal_model import Axiom
from api.providers.consistency_checker import (
    ConsistencyChecker,
    ConsistencyConflict,
    ConsistencyResult,
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
  "consistent": true | false,
  "conflicts": [
    {
      "axiom_label": "A-01",
      "description": "Kurze Beschreibung warum die Szene mit diesem Axiom konfligiert.",
      "suggestion": "Optional: Wie könnte Autor oder Axiom angepasst werden?"
    }
  ]
}

Wenn keine Konflikte vorliegen, ist "conflicts" eine leere Liste.
Antworte nur mit dem JSON-Objekt, ohne Erklärungen davor oder danach.\
"""


class ClaudeConsistencyChecker(ConsistencyChecker):
    """Adapter — uses Claude to check scene text against CausalModel axioms."""

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self._client = client

    async def check(self, scene_text: str, axioms: list[Axiom]) -> ConsistencyResult:
        """Sends the scene and axioms to Claude and parses the consistency verdict."""
        if not axioms:
            return ConsistencyResult(consistent=True)

        axiom_block = "\n".join(f"- {a.label}: {a.description}" for a in axioms)
        user_message = f"Szene:\n{scene_text}\n\nAxiome:\n{axiom_block}"

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
        conflicts = [
            ConsistencyConflict(
                axiom_label=k["axiom_label"],
                description=k["description"],
                suggestion=k.get("suggestion"),
            )
            for k in data.get("conflicts", [])
        ]
        return ConsistencyResult(consistent=data["consistent"], conflicts=conflicts)
