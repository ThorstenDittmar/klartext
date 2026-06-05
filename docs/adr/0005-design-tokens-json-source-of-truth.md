# ADR 0005: JSON als Source of Truth für Design Tokens

**Status:** Accepted  
**Datum:** 2026-06-05  
**Autoren:** Thorsten Dittmar

---

## Kontext

Das Frontend braucht ein Design System mit konsistenten Farben, Abständen, Typografie etc. Diese Werte müssen für drei verschiedene Zwecke zugänglich sein:
1. **Für Agenten** — maschinenlesbar, um Code zu generieren
2. **Für Designer/POs** — visuell, um Entscheidungen zu treffen
3. **Für den Browser** — als CSS Custom Properties zur Laufzeit

Die Frage ist: was ist die eine verbindliche Quelle und wie fließen die Werte zu den anderen?

---

## Entscheidung

**JSON-Dateien in `design/tokens/`** sind die einzige verbindliche Quelle für alle Design Token-Werte. Sie verwenden das W3C DTCG-Format (`$value`, `$type`).

**CSS Custom Properties** in `frontend/src/index.css` sind eine manuelle Kopie — sie müssen mit den JSON-Werten synchron sein, sind aber nicht die Quelle.

**Storybook** (wenn eingesetzt) ist ausschließlich Visualisierung — es liest die Tokens, definiert sie nicht.

---

## Begründung

**Für JSON als Source of Truth:**
- Maschinenlesbar für KI-Agenten (kein CSS-Parsing nötig)
- Versionierbar und diff-bar — Änderungen sind in Git sichtbar
- Tooling-agnostisch — kann in CSS, TypeScript, Storybook, Figma exportiert werden
- DTCG-Format ist interoperabel (Style Dictionary, Token Pipeline, Theo, etc.)

**Gegen CSS als Source of Truth:**
- CSS Custom Properties sind nicht strukturiert (kein Typ, keine Semantik-Metadaten)
- Keine maschinenlesbare Hierarchie (`color.semantic.green.bg` ist in CSS nur `--color-green-bg`)
- Für Agenten schwerer zu parsen als JSON

**Gegen Storybook als Source of Truth:**
- Storybook ist ein Visualisierungs-Tool, keine Datenbasis
- Zwei Quellen (Storybook + Code) würden unweigerlich auseinanderlaufen

---

## Konsequenzen

- Jede Token-Änderung beginnt in `design/tokens/*.json`
- Danach muss `frontend/src/index.css` manuell synchronisiert werden (bis Style Dictionary eingerichtet ist — siehe PENDING.md)
- Änderungen werden in `design/CHANGELOG.md` dokumentiert mit Verweis auf betroffene Komponenten
- Agenten lesen die Token-JSONs als Pflicht-ersten-Schritt vor jeder Frontend-Aufgabe

---

## Geplante Verbesserung

Style Dictionary soll mittelfristig `frontend/src/index.css` automatisch aus den JSON-Tokens generieren und den manuellen Sync-Schritt eliminieren (dokumentiert in `docs/superpowers/plans/PENDING.md`).
