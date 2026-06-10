# 0009 — Text-Editor-Strategie: TextArea statt Rich-Text-Editor

**Status:** Accepted  
**Datum:** 2026-06-08  
**Entscheider:** System Architect

## Kontext

Für die Manuskriptansicht (H01-B) wurde entschieden, dass Autoren Texte direkt im Browser bearbeiten. Drei Optionen wurden evaluiert:

- **Option A: Mehrere `<textarea>`-Elemente** (eine pro Fragment) — kein neues npm-Paket, kein Rich Text
- **Option B: TipTap (ProseMirror-basiert)** — Rich Text + Extensions; braucht `@tiptap/react`
- **Option C: `contenteditable`** — nicht empfohlen

Das Projekt verwendet ausschliesslich Inline-Styles (ADR-0004). Externe UI-Libraries setzen typischerweise auf CSS-Klassen.

Editing-Granularität: Text liegt auf `Fragment`-Ebene (Leaf-Node im Domänenmodell). Scene ist visueller Container, nicht Editing-Einheit.

## Entscheidung

**Option A (TextArea) — dauerhaft, nicht nur für Phase 1.**

TipTap ist nicht primär ein Abhängigkeits-Problem (neues npm-Paket), sondern fundamental inkompatibel mit ADR-0004:
- TipTap/ProseMirror injiziert aktiv CSS-Klassen (`.ProseMirror`, `.is-active`, `[data-placeholder]`) für Editor-State-Styling
- Diese Klassen sind nicht deaktivierbar — nur aggressiv überschreibbar
- Jedes TipTap-Update kann Styling-Regressionen einführen, die ADR-0004 konterkarieren

`contenteditable` (Option C) ist nicht empfohlen: Browser-Inkonsistenzen, komplexes Selection-Handling, schwierige Accessibility.

**Implementierungsmuster:**
- Eine `<textarea>` pro Fragment
- Debounce-Autosave (1,5 s Inaktivität oder `onBlur`)
- Scene rendert Fragmente als gestapelte TextAreas
- Save-Boundary = Fragment (kein ganzer Baum-Save für Textänderung)

## Konsequenzen

**Positiv:**
- Keine neuen npm-Abhängigkeiten
- Vollständige Kompatibilität mit ADR-0004
- Einfache, testbare Implementierung
- Auto-Save auf Fragment-Ebene: minimale Datenmenge pro Save

**Negativ / Einschränkung:**
- Kein Rich Text (fett, kursiv, Listen) — bewusste Einschränkung
- Wenn Rich Text später gewünscht wird: zuerst ADR-0004 neu bewerten, dann Editor-Entscheidung neu treffen — nicht umgekehrt

## Verwandte Entscheidungen

- ADR-0004: Inline-Styles-only (Voraussetzung dieser Entscheidung)
- ADR-0007: Eigene Komponentenbibliothek (dieselbe Begründung: externe Libraries kollidieren mit ADR-0004)
