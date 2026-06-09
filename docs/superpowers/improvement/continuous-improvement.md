# Kontinuierlicher Verbesserungsprozess (KVP) — Arbeitsweise des klartext Multi-Agent-Systems

> **Status:** Phase 1 in Arbeit · **Letzte Aktualisierung:** 2026-06-09 · **Pflege-Owner:** OE (vorläufig)
>
> **Dies ist ein lebendes Dokument.** Es ist der *eine* versionierte Ort, an dem wir unsere
> Arbeitsweise und ihre Verbesserung erfassen — damit es nicht die nächste Verluststelle wird.
> Kein einmaliger Schritt: am Ende steht ein dauerhafter Verbesserungs-Loop (§ KVP-Loop).

---

## 0. Zweck und Geltung

Nach dem ersten Sprint (H01) haben wir festgestellt, dass unsere Arbeitsweise systematische
Schwächen hat. Bevor wir Maßnahmen ergreifen, wollen wir **strukturiert und vollständig**
vorgehen — statt punktuell zu reagieren.

**Drei Risiken, gegen die dieses Dokument schützt** (vom User benannt):
1. **Verhäddern** — wir verlieren den Überblick über parallele Maßnahmen und ihre Abhängigkeiten.
2. **Nebenwirkungen übersehen** — eine Maßnahme verbessert A und beschädigt B, ohne dass wir es merken.
3. **Eigensaft** — wir erfinden Verfahren neu, die am Markt längst etabliert und erprobt sind.

**Leitprinzipien** (aus dem H01-Post-Mortem abgeleitet):
- **Nicht alles auf einmal.** Phasen statt Gleichzeitigkeit (das war ein H01-Kernfehler).
- **Jeder Schritt hat eine prüfbare DoD.** „Fertig" ist ein detektierbarer Zustand, kein Gefühl.
- **Vor Umsetzung: Machbarkeit gegen die Umgebung prüfen.** Unsere Werkzeuge (Claude Code, git,
  Supabase) schränken ein — Ideen müssen daran gespiegelt werden.
- **Kontinuierlich, nicht einmalig.** Der Prozess verbessert sich selbst weiter.

**Datenbasis:** Die Befunde aus dem H01-Post-Mortem, der Ablage-Inventur und die offenen
Entscheidungen liegen in `docs/superpowers/plans/PENDING.md` (Abschnitte „Post-Mortem H01 —
Coverage-Tracker", „Inventur-Befund", „Stand 2026-06-08"). Dieses Dokument baut darauf auf.

---

## 1. Definition of Done (baumartig)

Die DoD ist hierarchisch: Das Gesamtziel ist erreicht, wenn alle Phasen-DoDs erfüllt sind;
jede Phasen-DoD ist erfüllt, wenn ihre Kriterien erfüllt sind. Diese Struktur ist zugleich
die Gliederung des Projektplans (§ 2).

- [ ] **WURZEL — Das Multi-Agent-System verbessert sich verlässlich selbst.** *(North Star, 2026-06-09)*
  Tragender Pfeiler: **keine Erkenntnis geht verloren** — jedes Lernen wird festgehalten, *ohne dass jemand daran denken muss*. Verlustfreiheit, Nachvollziehbarkeit und Flow sind **Früchte** dieses Loops, keine separaten Ziele.

  > **Querschnitts-Prinzip — Enforcement-Hierarchie (gilt für JEDE Maßnahme/Regel):**
  > (1) **mechanisch** erzwingen wo möglich (Hook, pre-commit, CI, Branch-Protection) → (2) sonst als **festes Ritual** in einem definierten Workflow verankern (nicht dem Gedächtnis überlassen) → (3) **niemals advisory-only** (= der H01-Fehler).

  - [ ] **Der Loop läuft** (nicht „existiert auf Papier") und ist gegen **Capture-Verlust** gehärtet: jede Erkenntnis wird **mechanisch ODER rituell** festgehalten — nie nur advisory.
  - [ ] Jede beschlossene Maßnahme ist nach der Enforcement-Hierarchie verankert (mechanisch / rituell / nie advisory-only).
  - [ ] Dieses Dokument hat einen festen Pflege-Owner und wird nach jedem Sprint aktualisiert (= Teil des Loops, siehe § 3).
  - [ ] **Phase 1 — Problem- & Ursachenanalyse (RCA) vollständig** *(Gerüst)*
    - [ ] Alle Probleme aus H01 erfasst und kategorisiert (Quelle: Post-Mortem + Inventur)
    - [ ] Ursache-Folge-Ketten explizit erfasst (Ursache → Folge → Schaden), nicht nur Symptomliste
    - [ ] Jedes dokumentierte Symptom ist genau einer RC zugeordnet ODER explizit als *unerklärt* markiert (detektierbar — keine Lücke schweigt)
    - [ ] Die Gewerke-Bestätigung ist festgehalten (pro Gewerk), nicht nur im Chat erfolgt
  - [ ] **Phase 2 — Soll-Arbeitsweise erarbeitet (PM-Ebene)** *(Gerüst)*
    - [ ] Gewünschte Soll-Arbeitsweise beschrieben (wie *wollen* wir arbeiten) — inkl. des Loops selbst + der Enforcement-Hierarchie
    - [ ] Abgleich mit etablierten, hochstrukturierten PM-Methoden dokumentiert (mind. FDD, V-Modell; weitere nach Bedarf)
    - [ ] Abgleich mit modernen Ansätzen aus dem Vibe-Coding-/AI-Agent-Bereich dokumentiert
    - [ ] Synthese: was übernehmen wir, was verwerfen wir, **mit Begründung** (kein Eigensaft, keine blinde Übernahme)
    - [ ] Für jede Regel der Soll-Arbeitsweise ist die Enforcement-Stufe benannt (mechanisch / rituell) — keine bleibt advisory-only
    - [ ] Der Capture-Mechanismus selbst ist als konkretes Ritual oder mechanisch definiert (nicht „wir schreiben's halt auf")
  - [ ] **Phase 3 — Umsetzbarkeit geprüft** *(Gerüst)*
    - [ ] Umsetzungsplan für die Soll-Arbeitsweise steht
    - [ ] Machbarkeit gegen Umgebungs-Constraints geprüft (Claude Code, git/GitHub, Supabase, Hooks, Permissions)
    - [ ] Wo die Umgebung einschränkt: Anpassung dokumentiert (was geht nicht 1:1, was ist der Ersatz)
    - [ ] Nebenwirkungen je Maßnahme benannt (was könnte diese Maßnahme an anderer Stelle kaputt machen)
    - [ ] Pro Maßnahme bestätigt, welche Enforcement-Stufe die Umgebung *tatsächlich* hergibt; wo die höchste nicht geht, ist der Fallback dokumentiert (vgl. PreCompact-Hook: mechanisch ging nicht → Ritual)
  - [ ] **Phase 4 — Sequenzierung festgelegt** *(Gerüst)*
    - [ ] Reihenfolge/Roadmap steht: was gehen wir wann an
    - [ ] Keine „alles gleichzeitig"-Bündel; Abhängigkeiten explizit
    - [ ] Pro Schritt: Owner + prüfbare DoD
    - [ ] Die Reihenfolge respektiert die Wurzelursachen-Abhängigkeiten — z.B. erst Artefakt-Heimat (RC1), dann Gate darauf (RC2)

---

## 2. Projektplan (Phasen)

Wir arbeiten die Phasen **nacheinander** ab. Erst wenn die DoD einer Phase erfüllt ist,
beginnt die nächste. Jede Phase nennt: Ziel, Eingang (was wir brauchen), Ausgang (was entsteht),
Owner-Kandidaten.

**Aktueller Fahrplan (2026-06-09, User-bestätigt):**
1. Branch-Protection auf `main` + `ANTHROPIC_API_KEY`-Secret — *jetzt* (DevOps).
2. Safety-Commit der heutigen Arbeits-Schicht auf den Salvage-Branch — *jetzt*, nur sichern (DevOps).
3. **Phase 2 (Soll-Arbeitsweise)** — der nächste große Schritt.
4. **Salvage-Teardown bewusst NACH Phase 2** — Artefakte werden in die *dort neu definierte* Struktur platziert (einmal sauber statt zweimal). Begründung (User): „richtige Homes" sind erst nach Phase 2 bekannt, weil RC1/RC3 dort gelöst werden — vorher platzieren hieße nach dem alten/kaputten Modell sortieren.

### Phase 1 — Problem- & Ursachenanalyse (RCA)  ·  *Status: in Arbeit*
> **Begriffsklärung:** In *unserem* (Prozess-)Kontext heißt diese Analyse **Problem-/Ursachenanalyse (RCA)** — bewusst NICHT „Wirkmodell" oder „Wirkzusammenhang", um Verwechslung mit dem *fachlichen* Wirkgefüge/Wirkmodell des Produkts zu vermeiden.
- **Ziel:** Das Problem vollständig und als Ursache-Folge-Geflecht verstehen — nicht nur als Symptomliste.
- **Eingang:** Post-Mortem H01, Ablage-Inventur, Agenten-Feedback (alles in PENDING.md).
- **Ausgang:** Eine konsolidierte Problemlandkarte. Jedes Problem mit: Ursache → Folge → Schaden,
  und Verknüpfung zu den anderen (welche Probleme verstärken sich gegenseitig).
- **Owner-Kandidaten:** OE (Konsolidierung) + alle Gewerke (Bestätigung). Inhaltlich evtl. Hannibal.
- **Hinweis:** Vieles ist schon erhoben — diese Phase ist v.a. *Konsolidierung + Ursachenanalyse + Lückenprüfung*.

#### Problemlandkarte — RCA-Erstentwurf (2026-06-09)

> **STATUS: Phase 1 abgeschlossen (2026-06-09).** Sechs Wurzelursachen (RC1–RC6), user-validiert und durch **Gewerke-Gegenprüfung (8/8, pro Gewerk festgehalten)** bestätigt. Die Gegenprüfung ergab: RC6 neu (tacit assumptions), RC4 + RC5 erweitert (Lifecycle / Observability), RC3 geschärft (shared interfaces) — kein *unerklärtes* Symptom. Geparkt als Vorwärts-Fragen (keine Fehler): DevOps↔UX-Kanal, Technical Writer, B2-Schema-Check. **Alle vier Phase-1-DoD-Kriterien erfüllt.**

Datenbasis: Coverage-Tracker T1–T6, Inventur-Kategorien A–F, Triage-Funde (alles in `PENDING.md`). Ziel: nicht ~30 Symptome verwalten, sondern die *wenigen* Treiber darunter finden.

**Sechs Wurzelursachen (RC):** *(RC6 + RC4/RC5-Erweiterungen aus der Gewerke-Gegenprüfung, 2026-06-09)*

- **RC1 — Schlüssel-Artefakte ohne Zuhause.** *Ursache:* kein verbindlicher Ort/Format für Kontrakte, Sign-offs, Prozess-Schicht. → *Folge:* Entscheidungen leben im Chat / uncommitted / nirgends. → *Schaden:* nicht prüfbar, nicht rückverfolgbar, fast verloren. *Erklärt:* T1, Inventur-C, „Prozess-Schicht nie committed", Sign-offs nur im Chat.
- **RC2 — Regeln advisory statt erzwungen.** *Ursache:* gute Regeln als Text/Skill, aber kein Gate am Wirkort. → *Folge:* unter Druck vergessen/übersprungen. → *Schaden:* dieselben Fehler wiederholen sich. *Erklärt:* T6 (task-readiness nie aufgerufen), T2 (kein Integration-Gate), T3 (kein QA-Gate), Branch-Protection aus, negative Constraints nur in Memory.
- **RC3 — Owner-Modell unvollständig.** *Ursache:* Modell weist *Datei-Pfade* zu, nicht *Inhalte/Interfaces*; Querschnitt + Nähte ohne Owner; **shared/bidirektionale Interfaces ohne definierten Owner** (Konsument definiert *was*, Provider *wie* — die Naht dazwischen gehört niemandem). → *Folge:* Dinge fallen zwischen die Owner; Rollengrenzen sind nicht spürbar. → *Schaden:* unkoordinierte Änderungen, niemand pflegt's, Grenzübertritte. *Erklärt:* „Datei-Owner ≠ Interface-Owner" (Fakes, `.storybook`, `debug.py`, Cross-Domain-Fakes), Cross-Domain-Port nie eskaliert, Audit-Testdatei auf fremdem Branch, `.semgrep` flach (kein Owner pro Regel-Gruppe), **Hannibal zu tief (Rolle klar, aber Grenze nicht spürbar/erzwungen → auch RC2)**.
- **RC4 — „Aktiv" driftet gegen „abgelegt" + Artefakte/Abhängigkeiten ohne Lebenszyklus.** *Ursache:* kein Sync-Trigger zwischen laufendem Zustand (Session/DB/Installation) und Repo-Stand; **Artefakt-/Abhängigkeits-Typen haben kein Gültigkeits-/Verfalls-/Upgrade-Konzept** (erstellt, aber kein „wird ungültig wenn …"). → *Folge:* das Aktive divergiert still vom Aufgezeichneten; Artefakte altern unbemerkt. → *Schaden:* veraltete Permissions, verlorene Skills, Schema-Drift, stale Pläne, Modell-Upgrade ohne Governance. *Erklärt:* C1, Wrapper-Re-Install, Supabase-Drift, Token→CSS-Sync, `~/.claude` außerhalb Repo, **Plandokumente ohne Verfallsregel (UX/UI), Provider-Modell-Upgrade ohne Prozess (Audit)**. *(Remediation-Bezug: Artefakt-Register mit Lifecycle-Spalten.)*
- **RC5 — Prozess/Workflow nicht orchestriert (inkl. fehlendes geteiltes Lagebild).** *Ursache:* kein verbindlicher Dispatch-/Abhängigkeits-/Merge-Prozess; Rollen/Gates (QA, SA) nicht *by design* eingeplant, sondern nachgelagert; Pläne nicht gegen die Realität verifiziert vor Dispatch; **kein geteilter, verifizierter Ist-Zustand der Agents (Observability) — Koordination über mentale Modelle statt CI/Branch/PR-Status**. → *Folge:* paralleles Arbeiten kollidiert, Qualitäts-/Architektur-Kriterien entstehen zu spät, Pläne faktisch falsch, blinder Dispatch. → *Schaden:* Deadlocks, 5 Doppel-Commits, Salvage nötig. *Erklärt:* T5, T3 (QA als Nachgang), T4 (Plan stale/falsch), kein Merge-Owner, **Cross-Agent State Observability fehlt (DevOps — Hannibal dispatcht auf Annahmen statt verifiziertem Zustand; CI als Shared Source of Truth)**.
- **RC6 — Stillschweigende Annahmen/Kontrakte an Nähten werden nie SURFACED.** *Ursache:* es fehlt der Schritt *vor* dem Festhalten — implizite Input-Annahmen an den Domänen-Nähten werden nicht herausgezogen und als explizite, prüfbare Kandidaten auf den Tisch gelegt, *bevor* gebaut wird. *(Abgrenzung zu RC1: RC1 setzt voraus, dass das Artefakt gedacht wurde und nur keinen Ort hat — RC6 ist „ungeboren", nicht „heimatlos".)* → *Folge:* niemand prüft eine Annahme, die nie ausgesprochen wurde. → *Schaden:* **der 422** (Frontend nahm „API akzeptiert leeren content" an — nie artikuliert); fehlende Contract-Test-Schicht (man testet keinen Vertrag, den man nie benannt hat). *Erklärt:* 422-Kern (Hannibal), „Gate ohne Prüfraster" (SA — Reviews surfacen die Annahmen nicht), „Contract-Test-Schicht fehlt" (QA). *Owner des fehlenden Schritts:* Hannibal (schneidet Arbeitspakete, sieht die Nähte).

**Worked Example — der 422 war kein Zufall:** Kreuzung von **RC6** (die Annahme „API akzeptiert leeren content" wurde nie ausgesprochen) × **RC3** (die Naht hatte keinen Owner) × **RC5** (kein Prozessschritt „lies Backend-Schema vor Implementierung", kein Gate). Die Validierungsregel *existierte* sogar im Pydantic-Schema (also nicht primär RC1) — sie war nur nie als Kontrakt *surfaced*, *besessen* oder *geprüft*. Hätte *eine* der drei nicht gegolten, wäre er beim Schreiben aufgefallen statt beim User nach 1 Minute.

**Verstärkende Schleifen:**
- RC1 → RC2: Man kann nicht gaten, was kein Artefakt ist (kein Kontrakt → kein Kontrakt-Check). **Reihenfolge beim Beheben: erst Artefakt, dann Gate.**
- RC3 → RC5: Unklare Owner → Koordination bricht an den Nähten.
- RC1 ‖ RC4: Geschwister — „das Echte steht nicht im verlässlichen Record" (RC1: nie aufgezeichnet · RC4: aufgezeichnet, aber driftet).

**Gemeinsame Wurzel unter der Wurzel:** *Implizit/Konvention statt explizit/erzwungen/versioniert.* Das Betriebsmodell war als Dokumentation + guter Wille gebaut, nicht als besessene, dauerhafte, prüfbare Maschinerie. Alle **sechs** RCs sind eine Spielart davon. **Die Gegenprüfung hat das doppelt bestätigt:** die drei Frage-2-Funde sind selbst weitere Spielarten — implizite *Annahmen* (RC6), implizite *Gültigkeit* (RC4-Lifecycle), impliziter *Zustand* (RC5-Observability). Drei Gewerke haben die Wurzel unabhängig vertieft.

**Lücken-Check:**
- Schwach zugeordnet: „Hannibal zu tief" = RC2 (Rollengrenze advisory) + Koordinations-Vakuum (RC5); bewusst doppelt.
- Nicht RCA, sondern Vorwärts-Fragen (geparkt): „Technical Writer ja/nein", „DevOps↔UX Direktkanal" — „brauchen wir X?", keine „warum brach Y?".
- Offen für Gegenprüfung: Gibt es ein Symptom, das *keine* der fünf RCs erklärt?

**Gewerke-Gegenprüfung (DoD Phase 1: „pro Gewerk festgehalten") — gestartet 2026-06-09:**

| Gewerk | Status | Einwand / fehlendes Symptom |
|---|---|---|
| DevOps | ✅ RCs (mit Korrektur) | Korrektur: `.semgrep` flach → **RC3** (Owner-Modell), *nicht* RC4. **Frage-2-Fund:** *Cross-Agent State Observability* — kein geteiltes verifiziertes Lagebild; Hannibal dispatcht auf Annahmen statt CI/Branch-Zustand. Observability, nicht Orchestrierungs-Design (RC5). Kandidat; CI als Shared Source of Truth. |
| System Architect | ✅ RCs bestätigt | **Frage-2-Fund:** Sign-off war zeitlich korrekt, aber **Scope zu schmal** — kein erzwungenes Frageraster für Reviews (Tiefe hängt von Hannibals ad-hoc Frage, nicht von einem Standard). Kandidat: RC2 erweitern (Gate *ohne Prüfraster*) oder RC6. |
| QA | ✅ RCs bestätigt | T3→RC5 geteilt. **Frage-2-Fund:** *Fehlende Contract-Test-Schicht* zwischen Frontend-Unit (alles gemockt) und E2E (existiert nicht) — kein Test-Layer prüft den Vertrag. Fehlendes *Konzept* (Contract/Consumer-Driven Tests), nicht nur Owner/Prozess. |
| UX/UI | ✅ RCs bestätigt | **Frage-2-Fund:** Plandokumente **ohne Lebenszyklus/Verfallsregel** (Plan veraltet beim Phase-1-Merge, niemand merkt's) — fehlendes Artefakt-Lifecycle-Konzept. Präzisierung: 422 eher RC5+RC3 als RC1/RC3 (Kontrakt *existierte* im Schema, war nur nicht referenziert/ohne Owner). |
| Narrative | ✅ RCs bestätigt | **Frage-2:** kein Loch — alle Symptome erklärt. Branch-Kontamination → RC5 (Pfad-Überlappung). Nebenbefund: Semgrep-Gate fing `try/except`, aber erst beim Commit statt beim Planen (Gate am falschen Punkt). |
| Causal Model | ✅ RCs bestätigt | **Frage-2:** kein Loch. **RC3-Schärfung:** *Shared/bidirektionale* Interface-Ownership — wer owned das Interface *zwischen* Konsument (CM) und Provider (Audit)? Niemand; RC3 erklärt es evtl. zu schwach (mehr als „Datei-Pfad ≠ Interface"). Zusatz-Symptom RC2: committetes `# type: ignore` ohne blockierendes Gate. |
| Audit | ✅ RCs bestätigt | Korrektur: Model-ID in **4** Dateien (nicht 5). **Frage-2-Fund:** *Externe-Abhängigkeits-Lifecycle ohne Prozess* — wer entscheidet wann/nach welchen Kriterien Provider-Modelle upgraded werden? Kein Owner/Test/Sign-off. Lifecycle, nicht Drift. |
| Hannibal | ✅ RCs (mit Korrektur) | Korrektur: „Hannibal zu tief" → **RC3** (Rollen-/Owner-Disziplin, Grenze nicht spürbar → auch RC2), *nicht* RC5. **Frage-2-Fund (stark):** *Stillschweigende Annahmen an Nähten werden nie SURFACED* — der 422-Assumption war „ungeboren", nicht heimatlos. RC1 setzt Existenz voraus; hier fehlt der Schritt DAVOR (Annahmen explizit + prüfbar machen, bevor gebaut wird). Kandidat RC6. |

### Phase 2 — Soll-Arbeitsweise + Methoden-Abgleich  ·  *Status: geplant*
- **Ziel:** Definieren, wie wir arbeiten *wollen* (PM-Ebene), und das gegen erprobte Verfahren spiegeln.
- **Eingang:** Problem-Modell aus Phase 1.
- **Ausgang:**
  - Beschreibung der Soll-Arbeitsweise.
  - Abgleich mit **etablierten, hochstrukturierten PM-Methoden** — z.B. FDD (Feature-Driven
    Development), V-Modell, weitere nach Relevanz (Scrum/Kanban, SAFe, Shape Up …).
  - Abgleich mit **modernen Ansätzen aus dem Vibe-Coding-/AI-Agent-Bereich** (Marktrecherche —
    explizit gegen den Eigensaft).
  - **Synthese mit Begründung:** was übernehmen, was nicht, warum.
- **Owner-Kandidaten:** OE + Hannibal (PM-Methodik). Recherche evtl. mit Web-Recherche-Unterstützung.

**Instrument-Kandidat — Artefakt-Register** *(User, 2026-06-09):*
Eine *laufend gepflegte* Liste der **Artefakt-Typen** mit Metadaten — abzugrenzen von der einmaligen Ablage-Inventur (Problem-Snapshot). Spalten: Artefakt-Typ · Speicherort · Mengengerüst · Eigentümer · Konsument · Änderungshäufigkeit · Rituale/Prozesse die ihn nutzen · *(Kandidaten:)* Versioniert? (ja/nein/wo) · Enforcement-Stufe der Ablage.
**Wirkung:** adressiert RC1 (jeder Typ hat dokumentierten Ort), RC3 (Owner + Konsument explizit → „Datei-Owner ≠ Interface-Owner"), stützt RC2 (wo setzt der Guard an?) und RC4 (wo lohnt Drift-Check). → potenzielles **Zentral-Instrument**, nicht Nebenliste. Etabliertes Muster (Asset-Register / Daten-Katalog / CMDB-lite).
**Offen:** Spalten final · Ort · wer pflegt · Aktualisierungs-Ritual (das Register selbst muss gegen „veraltet" gehärtet sein — sonst driftet es, RC4 auf sich selbst).

**Vorgezogene Befunde (2026-06-09) — Kontext-/Memory-Management:**
Aus einer ersten Marktrecherche (Anthropic „Effective context engineering"; JetBrains Research; Claude-Code-Docs/Guides), ausgelöst durch die Compaction-Sorge:
- **Drei etablierte Techniken** (Anthropic): (1) **Structured Note-Taking / externes Gedächtnis** = laufend in durable Dateien schreiben (unser PENDING.md/claude.md) — die *primäre* Verlustschutz-Technik; CLAUDE.md überlebt Compaction (wird von Platte neu eingelesen). (2) **Proaktive Compaction an einer Schwelle** (~60 % Auslastung, mit Erhaltungs-Anweisungen) statt reaktivem Auto-Compact (~75–90 %). (3) **Sub-Agent-Architektur** = Kontext isolieren, nur Destillat zurückgeben.
- **Wichtige Klärung:** *pre-compact ≠ compaction.* Note-Taking **sichert** Wissen, schrumpft aber den Kontext nicht; Compaction **schrumpft**. Beide gehören gepaart (erst sichern, dann schrumpfen).
- **Trigger immer auslastungs-/turn-basiert, nie wanduhr-basiert.** Zu aggressive Kompression kostet am Ende mehr (Wiederbeschaffung).
- **Status quo bei uns:** Note-Taking ✅ (stark), Sub-Agents nur teilweise (Peer-Sessions isolieren Domänen-Kontext, aber der OE-Chat selbst lagert kaum aus), proaktive Schwellen-Compaction ❌ (fehlt).

**Offene Frage für die Soll-Arbeitsweise (vom User, 2026-06-09):**
Sub-Agents sparen Kontext (schlanker OE-Chat, seltener Compaction) **kosten aber User-Sichtbarkeit** und können echten Sessionkontext verlieren (vgl. „simulierter Hannibal" — bewusst verworfen). → Festlegen: **wo** Sichtbarkeit im Chat zählt vs. **wo** schlanker Kontext via Sub-Agent (nur Ergebnis) wichtiger ist. Faustregel-Kandidat: Sub-Agent für abgeschlossene, kontextarme Aufgaben (Recherche, breite Suche, „lies X → gib Schlussfolgerung"); Chat für alles, wo Aufsicht/echter Kontext zählt.

**Constraint-Fragen an DevOps (für Phase 3 — Machbarkeit) + Befund (2026-06-09):**
- **Kontext-%-Schwelle:** ❌/⚠️ UNKLAR. Kein dokumentierter %-Trigger. `autoCompactWindow` (Integer 100K–1M) existiert, aber Doku sagt nicht, ob es der *Trigger*-Schwellwert oder die *Zielgröße* nach Compaction ist → nur Experiment, kein verlässlicher Auto-Trigger.
- **PreCompact-Hook:** Snapshot ✅ · **Kontext/Anweisungen in Compaction injizieren ❌ (geht nicht)** · Block+Turn-Rückgabe ⚠️ nur via `exit 2` (Error-Feedback an Claude, *kein* sauberer Kuratierungs-Turn). `matcher: auto` vs. `manual` trennbar.
- **Auto-Persist:** technisch machbar (headless Shell-Hook schreibt Dateien), aber als Skill-Umbau/Parallel-Spur = **OE-Domain-Entscheidung**.
- **Folgerung:** Ein „goldenes" automatisches Kuratierungs-Gate vor Compaction ist in dieser Umgebung **nicht baubar**. Primärschutz bleibt **Note-Taking**; verfügbarer Quick Win = Snapshot/Audit-Hook (Backstop+Sichtbarkeit); proaktive Compaction bleibt **Disziplin** (kein nativer Auto-Trigger).

**Beschlossen (2026-06-09) — Compaction-Monitoring (Feedback-Mechanismus, kein Schutz):**
- **Hook** (DevOps, live 2026-06-09): schreibt pro Compaction `auto`/`manual` + Branch + ISO-Zeit in `.claude/compact-log.txt` (gitignored, lokal). Plus PreCompact-Transcript-Snapshot für `auto`-Events → `.claude/compact-snapshots/` (Heuristik, risikoarm). Teamweit via `.claude/settings.json` → erfasst alle Sessions; zeigt auch, *welche* Session am häufigsten an den Abgrund läuft.
- **Auswertung: lokaler Cron-Job (DevOps).** Prüft das Log in langsamer Kadenz auf neue `| auto |`-Einträge und alarmiert bei Fund; übergibt dann an OE + User für die Maßnahmen-Diskussion. = KVP-Loop Schritt 4 (Wirksamkeit prüfen). Häufige Auto-Compacts = Indikator, dass proaktiv nicht oft genug komprimiert wird. **Nachlaufendes Signal — misst, verhindert nicht.**

**Warum lokaler Cron (Begründung — bewusst dokumentiert):**
- **Nicht Cloud-Schedule:** Das Log ist projekt-lokal + gitignored → ein remote/Cloud-Schedule (klont nur das Repo) sieht die Datei nicht.
- **Nicht Session-Start-Ritual von OE:** Ein Cron läuft *unabhängig von jeder offenen Session* → fängt Auto-Compacts auch dann, wenn keine OE-Session aktiv ist (z.B. andere Agent-Sessions komprimieren, während OE schläft). Robuster als ein session-abhängiges Ritual.
- **Rollentrennung:** Der Cron *detektiert + alarmiert* (Skript); *Bewertung + Maßnahmen* bleiben bei OE + User.
- **IaC-Pflicht:** Die Cron-Definition gehört als Code ins Repo + Installation via `setup.sh` — **kein manuelles crontab-Edit**, sonst wäre der Cron selbst ein neuer untracked Drift-Punkt (vgl. C1 / Wrapper-Re-Install: „laufender Zustand vs. Repo-Stand").

**Konkrete Umsetzung (DevOps — live seit 2026-06-09, launchctl geladen):**
- **launchd** statt cron (cron auf macOS deprecated, überspringt Sleep-Zyklen). Agent: `~/Library/LaunchAgents/com.klartext.compact-monitor.plist`.
- **Kadenz:** stündlich (`StartInterval 3600`).
- **Alarm:** macOS-Notification (`osascript`) **+** Digest-Datei `.claude/compact-monitor-digest.txt` (gitignored) — Push + Pull; OE kann den Digest zusätzlich beim Session-Start lesen.
- **State:** Zeilenzähler in `.claude/compact-log-lastcheck` (gitignored), `wc -l`-Differenz → grep auf `| auto |`.
- **IaC:** `scripts/check-compact-log.sh` + `scripts/com.klartext.compact-monitor.plist.template` (`@@REPO_DIR@@`-Platzhalter) + `setup.sh`-Installation (`launchctl load`).
- **Notification-Framing:** nachlaufendes Signal („zu spät, künftig früher proaktiv komprimieren"), nicht „jetzt compacten".
- **Bekannte Einschränkung:** **macOS-only** — launchd existiert nicht in Codespace/Linux; dort läuft der Monitor nicht. Akzeptiert.

**TODO (offen, 2026-06-09) — pre-compact als Prozess-Schritt:**
- *Wann* soll pre-compact (Note-Taking-Sicherung) automatisch feuern? Kandidaten: Gute-Nacht-/Tagesabschluss-Nachricht, nach einer Retro, nach einem Commit/Merge, an natürlichen Schnittpunkten.
- *Wie* gestalten wir das **gefahrlos ohne Rückfragen an den User** (unbeaufsichtigter Auto-Persist: in Dateien schreiben ohne `AskUserQuestion`)? Berührt den pre-compact-Skill = OE-Domain; verknüpft mit DevOps-Befund Q3 (Auto-Persist-Modus).

### Phase 3 — Umsetzungsplan + Machbarkeit/Constraints  ·  *Status: geplant*
- **Ziel:** Prüfen, ob die Soll-Arbeitsweise in *unserer* Umgebung umsetzbar ist, und wo angepasst werden muss.
- **Eingang:** Soll-Arbeitsweise aus Phase 2.
- **Ausgang:**
  - Umsetzungsplan.
  - Machbarkeitsprüfung gegen Umgebungs-Constraints (Claude Code: Skills/Hooks/Sub-Agents/Cross-Session;
    git/GitHub: Branch-Protection/PR/CI; Supabase; Permissions).
  - Dokumentierte Anpassungen, wo die Umgebung einschränkt.
  - Nebenwirkungs-Analyse je Maßnahme.
- **Owner-Kandidaten:** DevOps (Umgebungs-Machbarkeit) + SA (Architektur-Verträglichkeit) + OE.

#### Bekannte Constraints & nötige operative Mechanismen (wachsende Liste)

**C1 — Agent-Refresh nach Skill-/`start.sh`-Änderung** *(User, 2026-06-09)*
- **Constraint:** Änderungen an Skills (`docs/superpowers/skills/`, `~/.claude/skills/`) oder an Start-Skripten (`agents/*/start.sh`) greifen erst nach einem **Neustart der betroffenen Agent-Session** — `claude.md`, Permissions und Skills werden beim Session-Start geladen. Eine laufende Session arbeitet mit dem alten Stand weiter.
- **Risiko:** Der Refresh wird nach einer Änderung vergessen → ein Agent arbeitet mit veralteten Permissions/Wissen weiter, ohne es zu merken. Tritt sicher wiederholt auf.
- **Nötiger Mechanismus (zu etablieren):** sicherstellen, dass nach einer solchen Änderung der Refresh angestoßen/erinnert wird. Kandidaten: (a) feste Bestandteil der Änderungs-DoD („Skill/`start.sh` geändert → betroffene Agents neu starten"); (b) ein Guard/Hinweis, der beim Schreiben in diese Pfade auf den nötigen Refresh aufmerksam macht; (c) Tracking, welche Sessions betroffen sind. Verwandt mit dem Wartungs-Haken „Wrapper-Re-Install / `klartext skills sync`" (Repo-Fähigkeit, PENDING.md) — beides ist „laufender Zustand vs. Repo-Stand driftet". Owner: OE (Prozess) + DevOps (ggf. technischer Reminder/Hook).

### Phase 4 — Sequenzierung / Roadmap  ·  *Status: geplant*
- **Ziel:** Festlegen, *wann* wir *was* angehen — bewusst gestaffelt.
- **Eingang:** Umsetzungsplan + Machbarkeit aus Phase 3.
- **Ausgang:** Roadmap mit Reihenfolge, Abhängigkeiten, Owner und prüfbarer DoD pro Schritt.
- **Owner-Kandidaten:** Hannibal (Planung) + OE.

---

## 3. KVP-Loop (dauerhaft)

Dieser Prozess endet nicht mit Phase 4. Die Verbesserung selbst wird ein wiederkehrender Takt:

- **Trigger:** Sprint-Ende (oder definierter Meilenstein).
- **Schritt 1 — Retro:** Was lief gut/schlecht? (Datenbasis: konkrete Vorfälle, nicht Eindrücke.)
- **Schritt 2 — Einspeisen:** Befunde fließen zurück in dieses Dokument (Problem-Modell § Phase 1 wächst).
- **Schritt 3 — Anpassen:** Soll-Arbeitsweise/Roadmap werden angepasst, wo nötig.
- **Schritt 4 — Wirksamkeit prüfen:** Hat eine frühere Maßnahme das Problem *wirklich* behoben? (Sonst zurück in den Loop.)
- **Owner:** OE pflegt den Loop; alle Gewerke liefern Input.

> Offen (mit User zu klären, in PENDING.md vermerkt): Brauchen wir ein explizites
> **Sprint-Anfang-/Ende-Flag** als Trigger für diesen Loop? Und: Wie verhindern wir, dass
> `/compact` mitten im Loop Wissen verliert?

---

## 4. Offene Punkte zu diesem Dokument selbst

- **Endgültiges Zuhause / mkdocs-Navigation:** Diese Datei liegt unter `docs/superpowers/improvement/`.
  Ob sie in die veröffentlichte Docs-Site (mkdocs-Nav) aufgenommen wird, berührt Infrastructure-Perimeter
  (DevOps) und die Docs-Struktur-Frage (SA) — beides aus dem H01-Post-Mortem noch offen. Bis dahin ist
  die Datei versioniert in git und damit gegen Verlust gesichert; die *offizielle* Einbindung folgt.
- **Pflege-Owner final bestätigen:** vorläufig OE.
