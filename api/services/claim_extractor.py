"""Claude API integration for claim extraction from narrative text."""

import json
import os
from typing import Any

import anthropic

_CLAIM_TYPEN = (
    "empirischer_claim | kausaler_claim | definitorischer_claim"
    " | normativer_claim | prognostischer_claim | kontrafaktischer_claim"
    " | methodischer_claim | unsicherheitsclaim"
)

SYSTEM_PROMPT = f"""Du bist ein Experte für epistemische Analyse narrativer Texte.

Deine Aufgabe: Extrahiere vorläufige Claims aus dem gegebenen Text.
Ein Claim ist eine behauptete Aussage –
empirisch, kausal, normativ, prognostisch oder definitorisch.

Antworte ausschließlich mit einem JSON-Array. Jeder Eintrag hat:
- "text": Die extrahierte Aussage (vollständiger Satz, max. 200 Zeichen)
- "typ": Einer von: {_CLAIM_TYPEN}
- "konfidenz": Float zwischen 0.0 und 1.0

Extrahiere nur Claims die explizit oder klar implizit im Text vorhanden sind.
Maximal 10 Claims pro Text. Claims sind vorläufig – nicht verbindlich."""


async def extract_claims_from_text(text: str) -> list[dict[str, Any]]:
    """Extract preliminary claims from narrative text via Claude API."""
    client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Extrahiere Claims aus folgendem Text:\n\n{text}",
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    claims = json.loads(raw)

    # Validate and clamp konfidenz
    for claim in claims:
        claim["konfidenz"] = max(0.0, min(1.0, float(claim.get("konfidenz", 0.5))))

    return claims
