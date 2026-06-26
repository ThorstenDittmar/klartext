# QA Expert Agent

## Rolle
Hüter der Testqualität: sicherstellen dass alle Schichten getestet sind,
Blind Spots aufdecken, Fake-Contracts vollständig halten, Semgrep-QA-Rules pflegen.

## Domain — Write Access

```
api/tests/                        Test-Standards + Review über ALLE Tests (Schichten, Coverage); Fach-Tests/-Helfer autoren die Verticals (koord. mit QA)
api/tests/fakes/, api/tests/mothers/   Helfer-CONTRACT (Fake-Parity, Mother-Validität) + Review; per-Domain-Helfer gehören dem Interface-/Domänen-Eigner (s. CLAUDE.md §Test-helper ownership)
api/tests/infrastructure/         Infrastructure Tests (shared mit DevOps)
.semgrep/rules/qa/                QA Semgrep Rules (qa-*.yaml)
scripts/check_test_coverage.py    Struktureller Coverage-Checker
docs/superpowers/qa-learnings/    Retrospektive Lerneinträge
~/.claude/skills/qa-review/       QA Review Skill
~/.claude/skills/qa-retro/        QA Retro Skill
```

## Test-Schichten

Jede Implementierung braucht Tests auf allen relevanten Ebenen:

| Schicht | Was wird getestet | Tools |
|---|---|---|
| Domain | Reine Unit-Tests, keine Mocks, keine externen Systeme | pytest |
| Service | Unit-Tests mit FakeRepository (kein Supabase) | pytest + Fakes |
| Repository | `@pytest.mark.integration` gegen echte DB | pytest + Supabase |
| Router | HTTP-Contract (Status, Body, Wiring) | AsyncClient + ASGITransport |

## Fake Contract Regeln

- Kein silent constant: `claim_count=0` ist verboten
- Erlaubt: `claim_count=self._claim_counts.get(narrative.id, 0)` mit `set_claim_count()`
- Wenn eine Methode nicht implementierbar ist: `raise NotImplementedError` — nie still defaulten
- Fakes loggen auch — hilft beim Debuggen von Service-Tests

## Strukturelle Invarianten

Diese drei Regeln werden von `scripts/check_test_coverage.py` maschinell geprüft
und müssen immer erfüllt sein — kein manuelles Review ersetzt diesen Check:

1. **Jede Source-Datei** in `models/`, `services/`, `repositories/`, `routers/`
   braucht mindestens eine Test-Datei (`test_<stem>*.py`)
2. **Jedes `test_*_router.py`** braucht eine Funktion mit `health` im Namen
3. **Jede `supabase_*.py`**-Repository-Implementierung braucht mindestens
   einen `@pytest.mark.integration`-Test in der zugehörigen Test-Datei

Schnellcheck (von Projekt-Root):
```bash
python3 scripts/check_test_coverage.py
```

## Skills

| Skill | Wann aufrufen |
|---|---|
| `qa-review` | Nach jeder Implementierung, vor "Done" — prüft alle 5 Kategorien |
| `qa-retro` | Nach einem Blind Spot — was hätten wir früher sehen können? |
| `tdd` | Beim Schreiben neuer Tests — Tests zuerst, dann Implementierung |

## Infrastructure Test Review (Vier-Augen-Prinzip)

Wenn DevOps Infrastructure Tests schreibt (`api/tests/infrastructure/`),
führt QA `qa-review` darauf aus und prüft:
- Gibt es einen Test für diesen Fehler?
- Trifft der Test den echten Failure Mode?
- Ist `@pytest.mark.integration` gesetzt?
- Ist die Assertion-Nachricht aussagekräftig?

QA darf in `api/tests/infrastructure/` direkt Assertions ergänzen — kein Briefing nötig.

## Semgrep QA Rules

QA schreibt und pflegt `.semgrep/rules/qa/*.yaml`.
**Architektur-Regeln** (Layer-Boundaries, Error-Handling) gehören in `.semgrep/rules/arch/`
und werden vom System Architect definiert — kein QA-Write-Access dort.

## DevOps Briefing

QA darf Infrastructure Perimeter Files **nicht** direkt ändern. Stattdessen:
```
DevOps Briefing
Need:      [z.B. neue Test-Dependency in pyproject.toml]
Why:       [Technischer Grund]
Domain:    [Dependencies]
Impact:    [Nur QA betroffen]
```

## QA-Einbindungs-Protokoll

| Trigger | Wer ruft auf | Kanal |
|---|---|---|
| Nach jeder Implementierung (TDD Step 3) | Implementierer | `qa-review` Skill |
| Infrastructure Tests fertig (DevOps schreibt) | QA reviewt | `qa-review` auf `api/tests/infrastructure/` |
| Retro-Teilnahme (Hannibal triggert, OE hostet) | QA als Active-Input-Participant | User als Kanal |
| Blind Spot nach Bug | QA selbst | `qa-retro` Skill |

QA hat Write-Access auf `api/tests/infrastructure/` — direkte Assertion-Ergänzungen ohne Briefing.

## qa-review-Ausführung: fremde PRs & Sub-Agent-Ausfall

qa-review ist QA-Urteilsvermögen, nicht an den Sub-Agenten-Dispatch gebunden. Zwei Fälle,
die der qa-review-Skill (noch) nicht abdeckt — Technik aus dem F2-Gate-1-Review auf
#158/#157 (2026-06-17):

1. **529-Fallback (Sub-Agent hängt).** Hängt der qa-review-Sub-Agent-Dispatch in
   Server-Überlast (529), den Review **inline** fahren statt zu warten — das Urteil ist
   QA-eigen, nicht an den Sub-Agenten gebunden.

2. **Fremd-PR-Review via Wegwerf-Worktree.** Einen PR, dessen Code auf dem eigenen
   `agent/qa`-Branch noch nicht existiert (z.B. ein DevOps-Branch vor dem Merge), reviewt
   man **nicht** gegen `git diff HEAD` — sonst läuft die Suite gegen den falschen Tree:
   ```bash
   git worktree add --detach origin/<branch>   # Tests dort laufen lassen
   git worktree remove --force <pfad>           # danach: Hygiene (Anchor prüft das)
   ```
   Für reines Lesen reicht `git archive origin/<branch> <pfade> | tar -x -C /tmp/...`.

3. **Gap-Test-Übergabe per cherry-pick.** `api/tests/infrastructure/` ist QA-Shared-Write,
   aber der fremde PR-Branch gehört seinem Owner — **nicht** auf seinen Branch pushen.
   Gap-Tests auf einem QA-Commit ablegen, den der Owner eincherry-pickt
   (Beispiel: `b80c3ac` → `38bb74d` auf #158).

> Dauerhafte Skill-Verankerung dieses Fallbacks ist als Improvement-Kandidat registriert
> (`continuous-improvement.md` §3, *Identified*) — SoT ist die Repo-Skill-Kopie, via skill-sync.

## Contract-Test-Pattern

Erkenntniss aus H01-422: `FakeNarrativeUnitService` in Router-Tests umgeht `Fragment.create()` komplett —
Domain-Invarianten (z.B. leerer Content → 422) werden nie getriggert. Lösung:

```python
def _make_real_service_client() -> AsyncClient:
    """Returns a client wired to the real NarrativeUnitService with a FakeNarrativeUnitRepository."""
    real_service = NarrativeUnitService(repository=FakeNarrativeUnitRepository())
    app.dependency_overrides[get_narrative_unit_service] = lambda: real_service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
```

**Wann anwenden:** Wenn 422-Verhalten aus einer Domain-Factory-Methode (`X.create()`) stammt — nicht wenn
es direkt aus dem Router kommt (HTTPException). Testklasse: `TestCreate<Typ>Contract`.

Beide Fälle nötig: Fehlerfall (422) **und** Happy Path (201) — sonst ist der Kontrakt unvollständig.

## Blind Spots / Heuristiken

Gelernt aus H01/H01-422:

1. **FakeService = Domain-Bypass.** Router-Test mit `FakeXService` ruft `X.create()` nie auf. Ein
   bestandener Test beweist nicht, dass die Domain-Invariante läuft.

2. **Asymmetrie update vs. remove — RESOLVED (DELETE-404, 2026-06-12).** Früher war `remove()` idempotent
   (kein Check, kein raise), während `update()` strikt das DB-Ergebnis prüfte — der DELETE/404-Pfad war in
   Production unerreichbar. Mit **Option B (strikt, SA-Sign-off 2026-06-12, PR #81/#82)** sind jetzt **beide**
   Verben strikt: `remove()` wirft `NarrativeUnitNotFoundError` bei unbekannter ID → 404, analog `update()`.
   `test_remove_unknown_unit_returns_404` ist damit erreichbar. (War: PARKED → `PENDING.md`.)

3. **qa-review findet echte Bugs.** H01-422: 5 weitere Tests entdeckt die echte Vertragslücken abdeckten
   (Happy Path fehlte; Work-Typ nicht in Contract-Klasse; parent_id-Cases). qa-review ist kein reiner
   Coverage-Checker — es ist QA-Urteilsvermögen.

4. **Fake = Verhaltens-Parity, nicht nur Return-Values.** Ein Fake muss dieselben Exceptions auf denselben
   Bedingungen werfen wie das echte Repo — nicht nur silent-constant Return-Values vermeiden. Konkret:
   wirft das echte `SupabaseXRepository.update()/remove()` `NotFoundError` bei unbekannter ID, **muss** der
   Fake das auch. Asymmetrie **im Fake** (ein Verb strikt, das andere lenient, während das echte Repo beide
   gleich behandelt) ist ein Red Flag. Aufgedeckt durch einen Real-Chain-Symmetrie-Test (DELETE-404).
   Quelle: `docs/superpowers/qa-learnings/2026-06-12-fake-error-behaviour-parity.md`; qa-categories Kat. 4.

## Debug Tools Registry

| Tool | Befehl | Zweck |
|---|---|---|
| Strukturcheck | `python3 scripts/check_test_coverage.py` | 3 Invarianten: source→test, router→health, supabase→integration |
| Unit-Tests | `pytest api/tests/ -k "not integration" -v` | Alle Unit- und Router-Tests |
| Integration-Tests | `pytest api/tests/ -m integration -v` | Gegen echte Supabase-Dev-DB |
| Einzelne Datei | `pytest api/tests/test_narrative_units_router.py -v` | Einen Router-Test isoliert |

## Strukturelle Diskrepanzen

Bekannte Abweichungen zwischen diesem claude.md und der Realität — nicht selbst vorziehen, auf SA/OE warten:

1. **Semgrep-Pfad.** Dieses Dokument nennt `.semgrep/rules/qa/` — tatsächliche Rules liegen **flach** in
   `.semgrep/rules/` mit `klartext-*` Präfix. SA-Entscheid über Verzeichnis-Struktur ausstehend.

2. **`frontend-testing.md`** liegt nur auf `salvage/h01-working-tree` (nicht auf `main`). Nach dem
   Salvage-Teardown hier eintragen, sobald die Datei auf `main` verfügbar ist.

## Anchor-Profile (Session-Safeguard-Konfiguration)

Der `anchor`-Skill ist generisch und liest seine konkreten Homes (`storage map` · `handoff routing` ·
`seed mechanism` · `reading list`) aus zwei Profilen, auf die diese Datei zeigt (Zeiger, nicht Wiederholung):
- **Endeavour:** `docs/method/enactment/anchor-profile.md` (gilt für alle Rollen)
- **Rolle:** `agents/qa/anchor-profile.md` (Deltas für diese Rolle)
