# H01 Post-Mortem — Gate-at-the-end ist kein Quality-by-Design

**Datum:** 2026-06-09
**Sprint:** H01 (NarrativeUnit Domain + ManuscriptView)
**Entdeckt durch:** OE Post-Mortem nach H01-B Phase 2 Gate (ROTES LICHT)

---

## Was ist passiert

QA war in H01 ausschließlich als Roundup-Gate eingebunden — erst nach abgeschlossener
Implementierung, nicht vor oder während der Planung. Die Konsequenzen:

- Test-Design-Entscheidungen (API komplett weggmockt, "tested manually" DODs)
  entstanden ohne QA-Input
- AutosaveStatus State-Machine (saving/saved/error) wurde nicht vollständig getestet
- Debounce-Pfad (`vi.useFakeTimers()`) fehlte komplett — kein Test assertierte
  dass `updateNarrativeUnit` nach dem Timeout aufgerufen wird
- Das Gate fand die Lücke, konnte aber nicht verhindern dass sie entstand

## Konkrete Lücke

`ManuscriptView.test.tsx` testete:
- ✅ typing → "unsaved" (synchron, einfach)
- ❌ nach 1500ms Debounce → "saving" + `updateNarrativeUnit` aufgerufen
- ❌ API-Erfolg → "saved"
- ❌ API-Fehler → zurück zu "unsaved"

Ein Test der `vi.useFakeTimers()` nicht importiert kann diese Übergänge nicht testen.

## Was sich ändert

**QA-Einbindungs-Protokoll** (in `agents/qa/claude.md` dokumentiert):

QA muss vor Implementierungsstart Prüfkriterien liefern, die direkt ins Plandokument
eingebaut werden. Format:

```
QA-Gate-Kriterien für [Feature]:
- [Konkreter Test der assertiert werden muss]
- Kein "tested manually" für persistierende Aktionen
```

Ohne diese Sektion im Plan: Plan ist nicht QA-freigegeben.

## Heuristik die daraus entstanden ist

**Für jeden Frontend-Gate:** "Wenn ich den API-Call durch `return undefined` ersetze —
bleiben alle Tests grün?" Wenn ja: der Mock deckt die Persistenz-Logik nicht ab.

**Für Pages mit Debounce:** `vi.useFakeTimers()` fehlt → mind. 2 von 3 Status-Übergängen fehlen.
Immer alle 3 prüfen: unsaved (sync), saving (nach timeout), saved (nach API-Erfolg).

## Verwandte Einträge

- `agents/qa/claude.md` — Abschnitte "QA-Einbindungs-Protokoll" und "Bekannte Blind Spots"
- `docs/superpowers/skills/frontend-testing.md` — Kriterien für Pages mit Autosave
