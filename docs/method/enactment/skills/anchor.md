---
name: anchor
description: >
  Anchor the session — secure everything that only lives in the chat to durable storage BEFORE
  context is lost (via /clear, /compact, or session end). Use whenever the user says "anchor",
  "session sichern", "nichts vergessen", "alles sichern", "vor clear", "vor neustart", "vor compact",
  or anything suggesting they want to checkpoint the session before context is reset. On a RESTART
  (generation change: next step is /clear and a successor session takes over) it also seeds the
  successor. Supersedes the former `pre-compact` skill — renamed because the ritual is no longer tied
  to /compact (the loss-free path is /clear; /compact only summarizes and is False-Persistence-prone).
---

# Anchor — Session Safeguard

Deine Aufgabe: die aktuelle Session systematisch durchgehen, **bevor der Kontext verloren geht** —
durch `/clear` (Generationswechsel, verwirft), `/compact` (fasst zusammen) oder Session-Ende. Ziel:
nichts Wichtiges verlieren — Entscheidungen, Begründungen, mündliche Anweisungen, offene TODOs, der
aktuelle Arbeitsstand. Der Name **anchor**: das flüchtige Chat-Wissen am festen Grund (Platte)
verankern; bei einem Restart zusätzlich einen Anker werfen, an dem die Nachfolge-Session wieder anlegt.

## Modus bestimmen (zuerst)

Kläre — fragen, wenn unklar: ist das ein **Restart** oder ein **Checkpoint**?

- **Restart** (Generationswechsel): als Nächstes kommt `/clear`, eine Nachfolge-Session übernimmt.
  → alle Schritte **inklusive Successor-Seed** (Schritt 4.6).
- **Checkpoint** (mid-session): du sicherst nur zwischendurch und arbeitest danach weiter.
  → Successor-Seed **überspringen** (sonst landen veraltete Handoff-Notizen im Postfach).

## Was einen Kontext-Reset überlebt

Diese Quellen sind sicher — sie liegen auf der Festplatte und werden bei jeder Session neu geladen:
- `CLAUDE.md` im Projekt-Root
- **Das Method-Dokumentenset**, seit der L2/L3-Trennung über zwei Stems verteilt:
  - **L2 (Enactment)** unter `docs/method/enactment/`: `continuous-improvement.md`
    (Entscheidungen + Begründungen + Improvement-Register §3), `method.md` (Element-Register),
    `learnings/` (Way-of-Working-Learnings), `environment/`
  - **L3 (Library)** generisch/Kernel unter `docs/method/library/`: `semat-definition.md` /
    `semat-glossary.md`, `alpha-states.md`, `practices/` (generische Practice-Karten; die
    klartext-Enactments liegen unter `docs/method/enactment/practices/`)
- `docs/superpowers/plans/PENDING.md` (Delegations-Tracking)
- `assets-local/README.md` (Provenienz-Register externer Referenzen)
- Memory-Dateien unter `~/.claude/`
- Code, Kommentare, Docstrings im Repo
- Commit-Messages in Git
- GitHub Issues und TODOs im Code
- Skill-Dateien unter `docs/method/enactment/skills/` (projekt-spezifische Skills) und `~/.claude/skills/` (User-Skills)

**Was verloren gehen kann:** Alles, was nur im Gesprächsverlauf steht. Das ist der blinde Fleck —
und `/clear` *verwirft* ihn ersatzlos, `/compact` *fasst ihn zusammen* (lückenhaft, False-Persistence-Risiko).

## Schritt 1 — Konversation scannen

Lies die gesamte bisherige Konversation durch. Sammle Kandidaten für jede dieser Kategorien:

1. **Architektur-Entscheidungen** — Strukturelle oder technische Entscheidungen die in dieser Session getroffen wurden
2. **Regeländerungen** — Neue Regeln oder Anpassungen an bestehenden Regeln, die noch nicht in CLAUDE.md oder Memory-Dateien stehen
3. **Begründungen (Warum)** — Erklärungen warum etwas so und nicht anders gemacht wurde
4. **Mündliche Anweisungen** — Anweisungen die der User im Chat gegeben hat, die aber nirgends schriftlich festgehalten sind
5. **Offene TODOs** — Angefangenes das nicht fertig ist, nächste Schritte, bekannte Probleme die vertagt wurden
6. **Arbeitsstand** — Was wurde in dieser Session abgeschlossen? Was ist in Arbeit? Was ist blockiert?
7. **Geparkte Befunde / Retro-Inputs** — Befunde die bewusst vertagt wurden (für eine Retro, einen
   Entscheid, ein anderes Arbeitspaket) und noch kein dauerhaftes Zuhause haben

Sei großzügig beim Sammeln. Lieber einen Punkt zu viel aufnehmen als einen zu übersehen.

## Schritt 1.5 — Delegations-/Befund-Check

**Trigger:** Nur ausführen, wenn es in dieser Session echt offene Delegationen oder ausgehende Befunde
gibt — sonst explizit überspringen ("Schritt 1.5: keine offenen Delegationen").

Für **Koordinations-Agents** (OE, Hannibal): Konversation nach **ausgehenden Delegationen** durchsuchen.
Für **Domain-Agents** ist das Muster stattdessen: **empfangene Tasks** (sind sie abgeschlossen oder
rückgemeldet?) und **ausgehende Befunde** (Dinge die ein anderer Agent wissen/entscheiden muss).
- Wissens-Briefings die an andere Agents formuliert wurden
- Aufgaben die an einen anderen Agent delegiert wurden
- Bitten an den User mit der Erwartung dass ein anderer Agent tätig wird
- Befunde aus der eigenen Arbeit, die an einen Owner außerhalb der eigenen Domain gehören

Für jede Delegation prüfen ob sie erledigt wurde:
1. Zieldatei lesen — ist die Änderung drin?
2. Gibt es eine explizite Bestätigung in der Konversation?

**Erledigt** → Reset ist sicher, kein Handlungsbedarf.

**Nicht erledigt** → Sub-Agent dispatchen der den Pending-Eintrag direkt schreibt:

```
Sub-Agent Auftrag:
Lies agents/<ziel-agent>/claude.md als Kontext.
Trage folgende offene Delegation in docs/superpowers/plans/PENDING.md ein,
Abschnitt "## Offene Delegationen", als neue Tabellenzeile:

| <Ziel-Agent> | <Aufgabe kurz> | <Dieser Agent> | <Datum heute> |
```

**Wichtig:** Sub-Agenten erben die Permissions des aufrufenden Agents.
Daher muss jeder Agent Write-Access auf `docs/superpowers/plans/PENDING.md` in seiner `start.sh` haben.

**Ausnahme:** Pending-Einträge werden **direkt geschrieben** — kein Briefing an den User nötig.
Das ist die einzige Ausnahme vom "User als Kanal"-Prinzip: hier geht es um Tracking, nicht um Domain-Wissen.

---

## Schritt 2 — Persistenzcheck

Für jeden gefundenen Punkt prüfen: Ist er bereits sicher gespeichert?
- In `CLAUDE.md`?
- Im Method-Set (`continuous-improvement.md` inkl. Improvement-Register, `method.md`, Glossar/Definition,
  `alpha-states.md`, einer Practice-Karte, `learnings/`)?
- In `PENDING.md` oder `assets-local/README.md`?
- In einer Memory-Datei?
- In einem Code-Kommentar oder Docstring?
- In einer Commit-Message?
- In einem GitHub Issue oder TODO-Kommentar im Code?

Jeden Punkt als **bereits gesichert** oder **noch nicht gesichert** markieren.

## Schritt 2.5 — Wissens-Routing

Für jeden noch nicht gesicherten Punkt aus Schritt 2 klassifizieren.

Zwei Fragen stellen — beide zählen:

> **1. Woher kommt das Wissen?** Liegt es in meinem Domain?
> **2. Wer hat fachliche Autorität darüber?** Wer entscheidet was hier "richtig" ist?

Frage 2 bezieht sich auf **Expertise und Autorität**, nicht auf Datei-Eigentümerschaft.
Beispiel: UX/UI entdeckt eine Lücke in den Verifikationskriterien → fachliche Autorität liegt bei QA
(auch wenn das Thema "Frontend" klingt und die Datei `verify.md` heißt).

Wenn Frage 2 einen anderen Agent nennt: mindestens Grenzwissen.

| Typ | Beschreibung | Konsequenz |
|---|---|---|
| **Eigenwissen** | Gehört in meinen Domain | → Schritt 3: normal speichern |
| **Fremdwissen** | Gehört vollständig zu einem anderen Agent | → Wissens-Briefing formulieren |
| **Grenzwissen** | Betrifft zwei Agents gleichzeitig | → je ein Wissens-Briefing pro Agent |
| **Organisationswissen** | Betrifft Struktur oder Zusammenarbeit | → Wissens-Briefing an OE |

Wissens-Briefing Format:
```
Wissens-Briefing an <Agent>
Typ:      [Fremdwissen / Grenzwissen / Organisationswissen]
Inhalt:   [Das konkrete Wissen — Entscheidung, Regel, Muster]
Kontext:  [Warum ist es entstanden? Aus welchem Problem?]
Ziel:     [In agents/<name>/claude.md eintragen, Abschnitt: ...]
```

Der User ist immer der Kanal — kein Agent schreibt direkt in die Dateien eines anderen Agents.

---

## Schritt 3 — Mit dem User durchgehen

Befunde klar und strukturiert präsentieren — auf Deutsch. Zuerst kurz bestätigen was bereits gesichert ist und wo.

Dann in zwei Blöcken:

**Block A — Eigenwissen** (gehört in meinen Domain):
Für jeden Punkt fragen:
- Muss das gesichert werden?
- Wenn ja: wo? Home nach Inhaltstyp wählen:
  - **Domain-Agents zuerst hier:** eigenes Hoheitswissen (Muster, Regeln, Heuristiken der eigenen Domain)
    → `agents/<name>/claude.md` · Domain-Learnings → das Learnings-Home der eigenen Domain
    (z.B. QA: `docs/superpowers/qa-learnings/`)
  - Entscheidung + Begründung zur Arbeitsweise → `continuous-improvement.md` *(via OE, wenn ohne Write-Access:
    Briefing formulieren)*
  - Prozess-Learning → `learnings/`
  - Neues/geändertes Methoden-Element → Practice-Karte + `method.md` (im selben Schritt; **nur OE** — andere
    Agents: Briefing an OE)
  - Begriff → Glossar: generischer Methoden-Begriff → `docs/method/library/semat-glossary.md` (L3);
    klartext-spezifischer Begriff → `docs/method/enactment/semat-glossary-klartext.md` (L2)
  - Verbesserungs-Kandidat → Improvement-Register (`continuous-improvement.md` §3; ohne Write-Access:
    Briefing an OE)
  - Geparkter Befund (Kategorie 7) → benanntes Verwahr-Depot mit Freigabe-/Löschbedingung (Memory-Park-Pattern)
  - Sonst: CLAUDE.md, Memory-Datei, Code-Kommentar, Commit-Message, neues Issue
- **Schreibrechte vorher prüfen:** Nur Homes wählen, auf die diese Session laut ihrer `start.sh` schreiben
  darf — sonst Briefing an den Owner formulieren statt still zu scheitern.
- Den konkreten Eintrag formulieren und dem User zeigen — **erst dann speichern wenn er explizit zustimmt**

**Block B — Wissens-Briefings** (gehört zu anderen Agents):
Alle formulierten Briefings präsentieren und fragen:
- Weiterleiten? Formulierung anpassen? Überspringen?
- **Niemals ohne Bestätigung weiterleiten**

Niemals auto-speichern. Immer auf Bestätigung warten.

**Wichtig:** Der User hat explizit gesagt, dass er es vorzieht zu viele Fragen gestellt zu bekommen als dass etwas übersehen wird. Im Zweifel fragen.

## Schritt 4 — Bestätigte Punkte speichern + Artefakt-Verifikation

Nach Bestätigung durch den User: Eintrag an der vereinbarten Stelle speichern. Passende Tools verwenden (Edit/Write für Dateien, Bash für git commits).

Wenn ein Eintrag in CLAUDE.md geht: Bestehenden Abschnitt aufrufen und passend einfügen — nie überschreiben, nie duplizieren.

**Pflicht-Abschluss — Artefakt-Verifikation (False-Persistence-Schutz):** Nach ALLEN Speicherungen
`git status` / `git diff --stat` (bzw. `ls -la` für Dateien außerhalb des Repos) ausführen und die
tatsächlich geänderten Dateien gegen die Liste der beabsichtigten Speicherungen abgleichen. **Der eigenen
Erinnerung oder einer Session-Summary wird nicht geglaubt — nur dem Artefakt.** (Beleg: 2× behaupteten
kompaktierte Summaries Schreibvorgänge, die nie stattfanden — RC4-Variante "False Persistence", 2026-06-10.)

## Schritt 4.6 — Successor-Seed (NUR im Restart-Modus)

**Überspringen, wenn Checkpoint.** Im Restart-Modus: eine Handoff-Notiz ins **eigene** Postfach legen,
damit die Nachfolge-Session ohne Lücke weitermacht (claude.md lädt die Identität, der Seed liefert den
*Stand*):

```
bash scripts/inbox.sh send <self> <self> "Successor-Seed: <kurzer Betreff>"
```

Inhalt der Notiz:
- **Stand:** was ist erledigt / in Arbeit / blockiert (mit PR-/Branch-/Commit-Bezügen)
- **Offene Fäden:** was als Nächstes ansteht, geparkte Befunde, wartende Briefings
- **Wake-Prompt:** eine konkrete erste Anweisung — eine frische Session handelt nicht von selbst,
  bevor der User die erste Nachricht gibt (Pilot-Lehre 2026-06-11)

**Artefakt-Verifikation auch hier:** prüfen, dass die Inbox-Datei tatsächlich existiert und nicht leer ist
(`inbox.sh unread <self>` / `wc -l` auf die Datei) — der Seed ist die Verlust-Versicherung, er darf nicht
selbst dem False-Persistence-Bug zum Opfer fallen.

## Schritt 4.7 — Worktree aktuell? (NUR im Restart-Modus, Hinweis)

**Überspringen, wenn Checkpoint.** Im Restart-Modus ist der Worktree nach Schritt 4 sauber (alles
committet) — ein sicherer Moment, ihn mit `main` zu synchronisieren, damit die Nachfolge-Session auf
aktuellem `main` startet (die App rebaset beim Start **nicht** automatisch — Drift-Lücke, siehe
Improvement-Register „App has no auto-rebase at session start").

Dieser Skill **rebaset nicht selbst** — er *verweist* nur auf das mechanische Tooling:
- `git rebase origin/main` (wenn der Worktree sauber ist und auf seiner `agent/<slug>`-Home-Branch sitzt), **oder**
- `klartext converge` (geguardeter Sync, sobald DevOps ihn ausliefert — die Aktions-Hälfte der Drift-Warnung).

**Nicht** auf einem Feature-Branch mit offenem PR zwangs-rebasen — der bekommt `main` beim PR-Merge.
Kosmetisch/optional: blockiert den `/clear` nie.

## Schritt 5 — Kurze Zusammenfassung

Kurze Zusammenfassung geben:
- Wie viele Punkte wurden gefunden
- Was war bereits gesichert
- Was wurde neu gesichert
- Was wurde bewusst übersprungen
- (Restart) ob der Successor-Seed liegt und verifiziert ist

## Schritt 6 — Prozess-Verbesserungen

> **Anbindung an die Methode:** Dieser Schritt ist ein *Capture*-Schritt, keine Retro — die eigentliche
> Bewertung gehört in die **Retrospective-Practice** (`docs/method/library/practices/retrospective.md`,
> generische Definition; klartext-Enactment: `docs/method/enactment/practices/retrospective.md`). Jeder hier gefundene
> Verbesserungs-Kandidat wird als **Improvement-Instanz ins Register** eingetragen
> (`continuous-improvement.md` §3, Zustand *Identified*) — nicht nur als loses TODO. Die nächste Retro
> priorisiert und bewertet.

### Teil A — Neue Skill-Kandidaten

Kurz fragen:

> *"Gab es in dieser Session etwas das sich wiederholt hat — eine Abfolge von Schritten, ein Muster, eine Aufgabe die du dir als wiederverwendbaren Skill vorstellen könntest?"*

Wenn ja: Kurz beschreiben was der Skill tun würde und festhalten. Der User entscheidet ob er den Skill jetzt oder später bauen will — kein Druck.

Wenn nein oder der User überspringen möchte: kein Problem.

### Teil B — Bestehende Prozess-Artefakte prüfen

Nur fragen wenn in der Session etwas Relevantes passiert ist — kein Pflicht-Protokoll:

1. **Bestehende Skills veraltet?**
   Hat ein Skill (`tdd`, `frontend`, `verify`, `anchor`) in dieser Session nicht geholfen, etwas Falsches vorgegeben oder war unvollständig? Wenn ja: was konkret ändern?
   → Sofort fixen oder als Improvement-Instanz ins Register (`continuous-improvement.md` §3)

1b. **Practice-Karten aktuell?**
   Hat sich in dieser Session geändert, *wie* wir arbeiten? Dann prüfen: stimmen die betroffenen
   Practice-Karten (L3-Definition unter `docs/method/library/practices/`, klartext-Enactment unter
   `docs/method/enactment/practices/`) und das Element-Register (`docs/method/enactment/method.md`) noch?
   → **Nur OE:** Karte(n) + `method.md` im selben Schritt aktualisieren (Maintenance-Ritual).
   → **Domain-Agents** (kein Write-Access auf `practices/`): Befund als Briefing an OE formulieren
   und dem User zeigen — Frage 1b damit erledigt, nicht überspringen.

2. **Tool-Config-Auffälligkeiten?**
   Gab es Linter-, Typecheck- oder Tach-Ausgaben die ignoriert oder umgangen wurden? Fehlt eine Konfigurationsregel die mehrfach hilfreich gewesen wäre?
   → Sofort in `ruff.toml`, `mypy.ini`, `tsconfig.json`, `tach.toml` etc. fixen oder als TODO
   → **⚠️ Infrastructure Perimeter:** `api/pyproject.toml` (ruff/mypy), `tach.toml`, `.pre-commit-config.yaml`, `.github/workflows/` und `frontend/`-Configs gehören zum Infrastructure Perimeter und dürfen nur vom DevOps-Agent direkt geändert werden. Wenn dieser Agent nicht DevOps ist: kein direkter Fix — stattdessen ein DevOps Briefing formulieren und dem User zeigen:
   ```
   DevOps Briefing
   Need:    [Was konkret geändert werden soll]
   Why:     [Technischer Grund]
   Domain:  [Dependencies / CI/CD / Config / Other]
   Impact:  [Welche Agents/Environments betroffen]
   ```

3. **Verify-Skills aktuell?**
   Wurden neue Screens, Komponenten oder API-Endpoints hinzugefügt? Dann prüfen: sind `docs/method/enactment/skills/verify.md` und `verify-backend.md` noch vollständig?
   → Skill-Datei direkt updaten wenn nötig

4. **GitHub Issues vollständig?**
   Wurden `TODO`-Kommentare im Code hinzugefügt ohne entsprechendes Issue? Wurden Issues in dieser Session implizit gelöst aber nicht geschlossen?
   → Issue anlegen oder schließen

5. **ADR nötig?**
   Wurde eine Architekturentscheidung getroffen die in `docs/adr/` festgehalten werden sollte? Format: `docs/adr/NNNN-kurztitel.md`, Status: `Proposed`.
   → ADR-Datei anlegen wenn der User zustimmt

---

**Abschluss:** Erst nach allen Schritten sagen, dass alles gesichert **und verifiziert** ist. Dann den
nächsten Schritt nennen — je nach Modus:

- **Restart:** *"Alles gesichert und verifiziert, Successor-Seed liegt. Du kannst jetzt `/clear` ausführen —
  verlustfreier Generationswechsel: `/clear` verwirft sauber, die Nachfolge bootet aus `claude.md` +
  liest den Seed."*
- **Checkpoint:** *"Alles gesichert und verifiziert. Du kannst weiterarbeiten."*

**`/clear` und `/compact` NIE selbst ausführen** — warten bis der User es explizit auslöst.

**`/clear` ist `/compact` vorzuziehen:** `/clear` *verwirft* (zwingt dazu, dass vorher wirklich alles
persistiert wurde — genau dieses Ritual), `/compact` *fasst zusammen* (lückenhaft, False-Persistence-Risiko).
Der Skript hieß früher `pre-compact`; umbenannt zu **anchor**, weil der Name an einen Befehl gebunden war,
der nicht mehr der bevorzugte Weg ist — `anchor` benennt das Wesen (Wissen verankern), nicht den Befehl.
