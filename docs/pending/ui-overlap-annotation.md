# Pending: Visuelle Darstellung von Overlapping Annotations

**Erstellt:** 2026-06-06
**Priorität:** Phase 2 — vor Implementierung der Volltext-Markierung
**Wartet auf:** Entscheidung durch UI Agent und Freigabe durch Autor

---

## Problem

Ein Textstück kann gleichzeitig ein Claim sein **und** einen Actor referenzieren.
Beide sind via `DocumentLink` mit demselben `DocumentNode` verbunden.

Im Volltext-Modus brauchen wir eine visuelle Konvention für diesen Fall.
Zwei übereinanderliegende Unterstreichungen in verschiedenen Farben wären
unleserlich und technisch schwierig darzustellen.

---

## Kontext

Die aktuelle Implementierung im Volltext-Modus zeigt:
- **Actors** mit grüner gepunkteter Unterstreichung (`#1D9E75`)
- **Claims** mit amber gepunkteter Unterstreichung (`#854F0B`)

Bei Überlappung entscheidet die Reihenfolge der `<mark>`-Tags, welche
Unterstreichung sichtbar ist — der andere Typ ist unsichtbar.

---

## Mögliche Ansätze

### Ansatz A — Priorität + Indikatorpunkt (empfohlen als Ausgangspunkt)
- Grüne Unterstreichung für Actor (Actor hat Priorität)
- Kleiner amber Punkt (`•`) unmittelbar nach dem markierten Text als
  Indikator dass hier auch ein Claim liegt
- Vorteil: lesbar, minimal, kein gestapeltes CSS
- Nachteil: Claim-Unterstreichung fehlt vollständig

### Ansatz B — Doppelte Unterstreichung mit Offset
- Actor: einfache gepunktete Linie, 2px unter dem Text
- Claim: einfache gepunktete Linie, 5px unter dem Text
- Technisch via `box-shadow` oder `text-decoration` mit Offset
- Vorteil: beide Typen sichtbar
- Nachteil: bei engem Zeilenabstand visuell überladen

### Ansatz C — Gemischte Farbe
- Bei Überlappung: weder grün noch amber, sondern eine dritte Farbe (z.B. Lila)
- Tooltip oder Kacheln zeigen dann beide Typen
- Vorteil: deutlicher Hinweis auf Überlappung
- Nachteil: neue Farbe muss in Design Tokens aufgenommen werden

### Ansatz D — Kein visueller Unterschied, nur Tooltip
- Überlappende Stellen werden genauso markiert wie Einzeltreffer
- Hover zeigt Tooltip mit beiden zugeordneten Objekten
- Vorteil: keine visuelle Komplexität
- Nachteil: Überlappung ist ohne Hover nicht erkennbar

---

## Offene Fragen

1. Wie häufig kommen Überlappungen in realen Narrativen vor?
   (Könnte sich als Randfall herausstellen)
2. Soll der User die Überlappung auf einen Blick erkennen können,
   oder reicht Hover/Click?
3. Gibt es eine bestehende Konvention im wissenschaftlichen Annotationsbereich?

---

## Nächste Schritte

1. UI Agent entscheidet sich für einen Ansatz (oder schlägt neuen vor)
2. Autor gibt Freigabe
3. Design Tokens ggf. erweitern
4. Implementierung in `NarrativeDetail.tsx` — `highlightText()` anpassen
