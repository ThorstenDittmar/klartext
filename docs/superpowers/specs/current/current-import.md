# Spec: Narrative Import — aktueller Implementierungsstand

**Datum:** 2026-05-29
**Status:** Implementiert
**Scope:** Import eines Narrativs aus einer Datei (.docx oder .md).
Beschreibt was heute im Code existiert.

---

## Überblick

Der Import liest eine Datei vom Server-Dateisystem ein, erkennt das
Format anhand der Dateiendung, delegiert das Parsen an den passenden
Parser und legt ein neues Narrativ mit den extrahierten Szenen an.

---

## Architektur

```
NarrativeImportService
  ├── NarrativeParser          (Port — für Textformate)
  │     └── MarkdownNarrativeParser
  └── NarrativeFileParser      (Port — für Binärformate)
        └── DocxNarrativeParser
```

Beide Ports sind abstrakte Interfaces (Ports-and-Adapters). Neue
Formate können als weitere Adapter hinzugefügt werden.

---

## NarrativeImportService

Verantwortlich für:
1. Prüfen ob die Datei existiert
2. Format-Dispatch nach Dateiendung
3. Szenen aus Parser-Ergebnis in ein Narrativ verpacken

```python
service.import_from_file(path: Path) -> Narrative
```

- `.docx` → `DocxNarrativeParser.parse_file(path)`
- alle anderen Endungen → Datei als UTF-8 lesen → `NarrativeParser.parse(content)`

**Fehler:**
- `NarrativeFileNotFoundError` — Datei existiert nicht
- `NarrativeParseError` — Datei leer oder keine Szenen gefunden

**Narrativ-Titel:** `path.stem` (Dateiname ohne Endung)

---

## MarkdownNarrativeParser

Erkennt Szenen anhand von `### Szene N`-Überschriften.

**Konvention:**
- Szenenüberschrift: `### <Titel>` (Markdown H3)
- Szenentrennlinie: `---` (wird aus dem Body entfernt)
- Alles vor der ersten `###`-Überschrift wird ignoriert

**Beispiel:**
```markdown
# Klartext
## Untertitel

---

### Szene 1

Hier beginnt der Text der Szene.

---

### Szene 2

Zweite Szene.
```

**Sonderfälle:**
- Szene ohne Body-Text → wird übersprungen
- Leerer Input → leere Liste (kein Fehler)

---

## DocxNarrativeParser

Erkennt Szenen anhand von Plain-Text-Absätzen die exakt dem Muster
`Szene <Zahl>` entsprechen (z.B. `Szene 1`, `Szene 15`).

**Grund:** klartext.docx verwendet ausschließlich `Normal`-Style-Absätze —
keine Word-Heading-Styles. Szenenmarker sind gewöhnliche Textzeilen.

**Konvention:**
- Szenentitel-Marker: Absatz dessen bereinigter Text `^Szene\s+\d+$` entspricht
- Alles vor dem ersten Marker wird ignoriert (Präambel: Titel, Untertitel)
- Leere Absätze innerhalb einer Szene werden verworfen
- Body-Absätze werden mit `\n\n` zusammengefügt

**Sonderfälle:**
- `Szene  2` (mehrere Leerzeichen) → gültiger Marker
- `Szene 1 – Der Abend` → kein Marker (gehört zum Body)
- Marker ohne nachfolgenden Body → Szene wird übersprungen
- Dokument ohne Marker → leere Liste (kein Fehler)

---

## API-Endpunkt

```
POST /narratives/import
Body: {"path": "/absoluter/pfad/zur/datei.docx"}
```

- Pfad bezieht sich auf das Server-Dateisystem (nicht auf den Client)
- Gibt das vollständige Narrativ-Objekt zurück (HTTP 201)
- Unterstützte Formate: `.docx`, `.md` und andere Textformate

---

## Was fehlt (bewusste Vereinfachungen)

- Kein Datei-Upload vom Browser (nur Server-Pfad)
- Kein `.scriv`-Import (Scrivener-Format)
- Kein automatischer Titel aus dem Dokument-Inhalt — immer `path.stem`
- Keine Erstanalyse nach Import (vorgeschlagene Wirkmodelle, vorläufige Claims)
- Kein Import-Update (erneuter Import einer Datei legt immer ein neues Narrativ an)
