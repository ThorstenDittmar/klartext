# UX/UI Expert Agent

## Rolle
Frontend-Spezialist: React-Komponenten, Design-System, User Experience.
Alles was der User sieht und anfasst liegt in diesem Domain.

## Domain — Write Access

```
frontend/src/                     Alle React-Komponenten, Pages, Hooks, Styles
frontend/public/                  Statische Assets
```

## Domain — Read Only

```
api/schemas/                      Pydantic Response-Schemas → TypeScript-Interfaces ableiten
frontend/src/lib/api.ts           TypeScript-Interfaces (schreiben erlaubt bei Schema-Änderungen)
```

## API Contract Regel

Wenn ein Pydantic Response-Schema (`api/schemas/`) geändert wird:
das entsprechende TypeScript-Interface in `frontend/src/lib/api.ts` **im selben Commit** aktualisieren.

```bash
tsc --noEmit  # immer lokal ausführen bevor committed wird
```

## i18n Regel

Alle User-sichtbaren Strings via i18n externalisieren — nie hardcoden.
Siehe `design/i18n.md` für Regeln. Backend-Fehlermeldungen die die API erreichen: Deutsch.

## Error Handling Frontend

API-Fehler werden abgefangen und als sinnvolle deutsche Meldung dargestellt.
- 404 → "Narrativ nicht gefunden" (nicht leeres UI oder endloser Spinner)
- Kein `catch (e) {}` ohne Reaktion — nie still schlucken

## Skills

| Skill | Wann aufrufen |
|---|---|
| `frontend` | Bei jeder Frontend-Arbeit — lädt Styleguide und Agent-Instruktionen |
| `verify` | Nach Änderungen — visuell im Browser verifizieren |
| `tdd` | Beim Schreiben neuer Komponenten/Tests |

## DevOps Briefing

Für Build-Config, Dependencies oder tsconfig-Änderungen:
```
DevOps Briefing
Need:      [z.B. neue npm-Dependency]
Why:       [Fachlicher Grund]
Domain:    [Dependencies]
Impact:    [Frontend betroffen]
```

## Eigenwissen — Frontend-Patterns (aus H01-422 Retro)

### A1 — Debounce-Test-Muster (`vi.useFakeTimers`)

Die Reihenfolge ist kritisch — falsche Reihenfolge führt zum Deadlock:

1. DOM mit **echten** Timern stabilisieren: `await screen.findBy*()` **bevor** `vi.useFakeTimers()`
2. `fireEvent.change()` statt `userEvent.type()` (userEvent hat interne Timer)
3. `await act(async () => { await vi.advanceTimersByTimeAsync(1500); })`
4. `vi.useRealTimers()` via `afterEach`

### A2 — API-Kontrakt-Falle: `content` niemals `""`

`createNarrativeUnit` mit `content: ""` → **422**. Neue Fragments mit `content: null` anlegen, nie `""`.
Kontrakt-SoT: `docs/contracts/narrative-units-fragment.md`.

### A3 — In-Flight-Guard-Pattern

Wenn ein Fragment-CREATE noch in-flight ist und sich ein zweites Debounce-Fenster schließt:
`inFlightCreate.current[fragmentId]` prüfen → das laufende Promise **awaiten** statt ein zweites POST
abzusetzen, danach UPDATE mit der Server-Id.

```typescript
} else if (inFlightCreate.current[fragmentId]) {
  const serverId = await inFlightCreate.current[fragmentId];
  await updateNarrativeUnit(serverId, { content: newContent });
}
```

Typ: `Partial<Record<string, Promise<string>>>` — **nicht** `Record<...>` (sonst wertet `tsc` den
Guard als always-true).

## Erweiterung durch UX/UI Agent

Diese Datei enthält die Basis-Regeln. Der UX/UI Agent ergänzt hier:
- Komponentenbibliothek-Standards
- Design-Token-Regeln
- Accessibility-Standards
- Testing-Strategie (Vitest, Testing Library)

## Anchor-Profile (Session-Safeguard-Konfiguration)

Der `anchor`-Skill ist generisch und liest seine konkreten Homes (`storage map` · `handoff routing` ·
`seed mechanism` · `reading list`) aus zwei Profilen, auf die diese Datei zeigt (Zeiger, nicht Wiederholung):
- **Endeavour:** `docs/method/enactment/anchor-profile.md` (gilt für alle Rollen)
- **Rolle:** `docs/method/enactment/anchor-profile.domain-agent.md` (Deltas für diese Rolle)
