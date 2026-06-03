# Wirkgefüge — Designprinzipien

Leitende Prinzipien aus der Konzeptionssession. Noch nicht ins Projekt integriert.
Werden später in CLAUDE.md und Projektdokumentation eingearbeitet.

---

## Keine Wahrheitsmaschine

Die Plattform bewertet nicht, ob Inhalte empirisch wahr sind. Sie prüft ausschließlich
die interne Konsistenz, Vollständigkeit und Transparenz von Modellen.

Konsequenzen:
- `EpistemicStatus` beschreibt den Transparenzstatus eines Elements, nicht seine externe Wahrheit
- Kontrafaktische, spekulative oder fachlich randständige Modelle sind zulässig, sofern ihre Annahmen explizit sind
- Claims über empirische Evidenz werden nicht durch die Plattform bewertet — Evidenz ist informativ und wird über `Source`-Referenzen eingebunden

## Alle semantischen Operationen laufen top-down

CausalComponents sind kontextfrei — sie kennen ihren Container nicht. Alle semantischen
Operationen (Namespace-Auflösung, Scope-Prüfung, Vollständigkeitsprüfung, Prüfverfahren)
starten immer am Container und traversieren nach unten.

Konsequenzen:
- Kein `_container`-Attribut auf CausalComponent
- Eine Component kann in mehreren Containern gleichzeitig leben (insbesondere CausalMixin)
- `resolve(identifier)` wird immer am CausalModel aufgerufen, nicht an der Component
- Prüfverfahren starten immer an CausalModel oder CausalModelFederation

## Code immer auf Englisch

Alle Bezeichner (Klassen, Methoden, Variablen, Attribute) sind Englisch.
Kommunikation mit dem User auf Deutsch.

## Explizitheit über Implizitheit

Interpretative Entscheidungen dürfen bei der Modellbildung getroffen werden,
dürfen aber im fertigen Wirkgefüge nicht als unaufgelöste Mehrdeutigkeit verbleiben.
Mehrdeutigkeiten müssen als Varianten, Konflikte, Lücken oder offene Fragen
explizit ausgewiesen werden.
