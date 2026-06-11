# Lagebild für eine externe Zweitmeinung — Multi-Agent-Setup „klartext"

> **Zweck dieses Dokuments.** Der Projektinhaber holt eine externe Meinung zu unserem
> Multi-Agent-Arbeitsmodell ein. Dieses Dokument beschreibt das Setup, die Arbeitsweise,
> die aufgetretenen Probleme, den Lösungsstand und das Zielbild — so vollständig, dass
> es ohne weiteres Vorwissen beurteilbar ist.
> **Stand:** 2026-06-10, Abend. **Autor:** OE-Agent (Method Keeper), reviewt vom Projektinhaber.

---

## 1. Das Projekt

**klartext.jetzt** ist eine Webanwendung (Monorepo: FastAPI-Backend, React/TypeScript-Frontend,
Supabase-Datenbank) rund um Narrative, Behauptungen (Claims) und kausale Wirkmodelle
(„Wirkgefüge"), inklusive einer Manuskript-Editieransicht. Ein einzelner menschlicher
Projektinhaber entwickelt es mit einem Team aus **10 spezialisierten KI-Agenten**
(Claude-Sessions). GitHub-Flow mit PRs, Branch-Protection und CI (6 Checks) ist etabliert.

## 2. Das Team-Setup

### 2.1 Die 10 Agenten

| Agent | Rolle |
|---|---|
| **Hannibal** | Projektleiter / Arbeitspaket-Koordination (schneidet Tasks, dispatcht, verantwortet Merge-Reihenfolge) |
| **OE** (Organisationsentwicklung) | Method Keeper: pflegt die Arbeitsweise (SEMAT/Essence-basiert), hostet Retrospektiven, verbessert das *Team*, nicht das Produkt |
| **DevOps** | Alleiniger Owner des „Infrastructure Perimeter" (CI/CD, Configs, Tooling, git-Mechanik) |
| **System Architect** | Architekturentscheidungen, ADRs, Interface-Kontrakte, Sign-offs |
| **QA** | Teststrategie (4 Ebenen), Verifikationskriterien, QA-Reviews |
| **UX/UI** | Design-Tokens, Komponenten-Specs, eigene Komponentenbibliothek (Inline-Styles-only per ADR) |
| **Narrative Expert** | Fachdomäne Narrative/Manuskripte |
| **Causal Model Expert** | Fachdomäne Wirkgefüge/Kausalmodelle |
| **Audit Expert** | Fachdomäne Claims/Belege |
| **Community Expert** | Fachdomäne Community-Funktionen |

### 2.2 Long-living Sessions („ewige Agenten")

Jeder Agent ist **eine einzige, dauerhaft laufende Session** der Claude-Desktop-App
(macOS), gestartet vor Tagen, **nie neu gestartet**. Neue Sessions entstehen nur, wenn
ein neuer Teamkollege angelegt wird — auch der lebt dann „ewig". Konsequenzen:

- Das **Kontextfenster der Session ist das Arbeitsgedächtnis** des Agenten. Es wächst,
  bis eine Compaction (Zusammenfassung des Verlaufs) nötig wird — kontrolliert
  (`/compact` durch den User) oder **unkontrolliert** (Auto-Compact bei voller
  Kontextlänge). Unkontrollierte Compaction ist unser gefährlichster Verlustmodus.
- Identität, Hoheitswissen und Regeln jedes Agenten liegen in einer versionierten Datei
  `agents/<name>/claude.md` — das ist das, was eine Compaction oder einen Neustart überlebt.
- Pro Agent existiert ein `agents/<name>/start.sh` (Terminal-Start mit `cd` ins Repo und
  deklarierten Tool-Permissions). **Befund von heute: Diese Skripte wurden nie benutzt** —
  alle Sessions liefen immer über die Desktop-App aus dem Home-Verzeichnis (Details §5.4).

### 2.3 Kommunikationsmodell

- **Grundregel: Der User ist immer der Kanal.** Kein Agent schreibt in die Dateien eines
  anderen Agenten; Wissen, das die Domäne wechselt, wird als „Wissens-Briefing" formuliert
  und vom User zugestellt.
- **Direct Messages** zwischen Sessions (App-Funktion `send_message`) sind als Transport
  erlaubt, aber **pro Einzelfall user-genehmigt** (jeder Versand erfordert eine Bestätigung).
  Das hat sich heute als tragende Infrastruktur erwiesen: Freigaben, Befund-Relays,
  Team-Briefings liefen darüber.
- **Koordination:** Hannibal schneidet Arbeitspakete und dispatcht an die Fach-Agenten
  (per Direct Message, user-vermittelt). OE beobachtet methodisch und hostet danach die
  Retrospektive (Vier-Augen-Prinzip: Koordinator triggert, Method Keeper hostet).

### 2.4 Wann wir Subagents forken

Subagent-Forks (ephemere Kind-Instanzen einer Session) nutzen wir **sparsam und nur für
abgegrenzte Schreib-/Prüfaufträge**, nie als Ersatz für die lebenden Kollegen:

- Im **Pre-Compact-Ritual**: Ein Subagent trägt offene Delegationen in das zentrale
  Tracking (`PENDING.md`) ein.
- Im **QA-Review**: Ein Subagent prüft Testabdeckung/Edge-Cases nach Implementierungen.
- Subagents erben die Permissions der aufrufenden Session — was heute zur Entdeckung
  beitrug, dass die deklarierten Permissions gar nicht wirken (§5.4).

Wichtig: Die Vertretung eines *Kollegen* durch einen Subagent-Fork (z. B. in einer Retro)
ist nur zulässig, wenn dessen Wissen vorher nachweislich auf Platte gesichert wurde
(„Capture-Vorbedingung") — sonst ist eine Live-Beteiligung der echten Session Pflicht.

## 3. Die Arbeitsweise (Methoden-Schicht)

Wir arbeiten explizit methodengeführt auf Basis von **Essence/SEMAT** (Kernel-Alphas,
Practices, Zustandsmodelle). Der Method Keeper (OE) hält ein versioniertes Dokumentenset:

- `docs/superpowers/improvement/continuous-improvement.md` — Entscheidungen mit Begründung
  + **Improvement-Register** (§3 dort): jede Verbesserung als Instanz mit Lebenszyklus
  *Identified → Prioritized → Action Agreed → Trialed → Results Evaluated → In Use*.
  Aktuell ~30 Instanzen, vom Erstfund bis zur geschlossenen Maßnahme.
- `method.md` — Element-Register aller Practices/Patterns/Work Products, inkl.
  **Non-Negotiable-Flags** und einer „Enforcement-Hierarchie" (mechanisch > rituell >
  nie nur beratend).
- Practice-Karten (`practices/`), z. B. Retrospektive (Entry-Kriterien, Teilnehmerregeln,
  Abweichungsklausel) und Merge-Protokoll (benannter Merge-Owner, explizite Reihenfolge,
  Artefakt-Verifikation).
- `learnings/` — Prozess-Learnings pro Ereignis; `plans/PENDING.md` — Delegations-Tracking;
  ADRs unter `docs/adr/`.

Entwicklung läuft mit TDD (Tests vor Implementierung), strenger Schichtenarchitektur,
PR-Gates und einem „Task-Readiness"-Check vor jeder Umsetzung. Der Status der Arbeitsweise
ist formal getrackt: Das Way-of-Working-Alpha steht seit heute auf **In Use** (alle 9
Kollegen haben die Methode in einem Team-Refresh explizit bestätigt).

**Rituale gegen Kontextverlust:**

- **Pre-Compact-Skill** (Pflicht vor jeder Compaction): Session systematisch scannen —
  Entscheidungen, Begründungen, mündliche Anweisungen, offene TODOs — und alles
  Ungesicherte in die richtigen Homes schreiben, mit **Artefakt-Verifikation**
  (`git status`/`git diff` nach dem Schreiben; Erinnerung und Summaries gelten nicht
  als Beweis).
- **Wissens-Routing**: Bei jedem Pre-Compact wird geprüft, ob Erkenntnisse in fremde
  Domänen gehören → Briefing statt Selbst-Schreiben.
- **Memory-Park-Muster**: Ungesicherte Funde werden notfalls in einem benannten Depot
  im Auto-Memory geparkt, mit expliziter Lösch-/Freigabebedingung.

## 4. Speicherorte — heute und gewollt

### 4.1 Was wo liegt (heute)

| Inhalt | Ort | Status |
|---|---|---|
| Produkt-Code, Tests, CI | Repo (`api/`, `frontend/`, `.github/`) | ✅ stabil, PR-Gates |
| Methode (Register, Karten, Learnings, ADRs) | Repo (`docs/superpowers/`, `docs/adr/`) | ✅ versioniert; ⚠️ Edits reiten teils uncommitted im Shared Tree |
| Agenten-Identität/Hoheitswissen | Repo (`agents/<name>/claude.md`) | ✅ versioniert; ⚠️ gleiche Shared-Tree-Gefahr |
| Team-Gedächtnis (Auto-Memory) | `~/.claude/klartext-team-memory/` (seit heute explizit gepinnt; vorher zufällig cwd-gekeyt) | ✅ bewusst geteiltes „Blackboard" aller Sessions |
| Session-Kontext (Arbeitsgedächtnis) | nur im Kontextfenster | ⚠️ flüchtig; einziger Schutz: Pre-Compact-Disziplin |
| Tool-Permissions pro Agent | `agents/<name>/start.sh` | ❌ **wirkungslos** (Skripte nie benutzt, §5.4) |
| Projekt-Hooks/-Settings | `klartext/.claude/settings.json` | ❌ **laden nie** (Sessions starten in `$HOME`, §5.4) |

**Architektur-Eigenheit:** Alle 10 Agenten arbeiten auf **einem gemeinsamen Working Tree**
(`/Users/thormar/klartext`). Branch-Operationen eines Agenten treffen uncommittete
Änderungen aller anderen (§5.2).

### 4.2 Wie wir speichern wollen (Zielbild)

1. **Alles Dauerhafte versioniert im Repo**, in klaren Homes pro Inhaltstyp — das steht
   und funktioniert; offen ist die Idee, die drei Commit-Klassen (Produkt /
   Prozess-Stand / Methoden-Artefakte) in der CI zu entkoppeln.
2. **Uncommittete Arbeit darf nie durch fremde git-Operationen sterben** — gewünschte
   Lösung: Isolation pro Agent (Worktree o. Ä.), bis dahin rituelle Schutzregeln.
3. **Team-Gedächtnis explizit statt zufällig**: ein benanntes, geteiltes Memory-Verzeichnis
   (seit heute umgesetzt), perspektivisch projekt- statt maschinenweit konfiguriert,
   mit noch zu definierenden Ownership-Konventionen.
4. **Session-Kontext als abgesicherte Ressource**: Compaction beobachtbar (Monitoring),
   planbar (proaktive Schwellen-Compaction statt Auto-Compact) und verlustarm
   (Pre-Compact als erzwungener Schritt, nicht nur Ritual).
5. **Permissions/Boundaries mechanisch durchgesetzt statt nur dokumentiert.**

## 5. Die Probleme — chronologisch und ehrlich

### 5.1 Erster Durchlauf „H01" (Post-Mortem)

Unser erstes größeres Arbeitspaket lief schief und wurde vollständig obduziert. Die
Wurzelursachen (RC1–RC6), stark verkürzt:

- **RC1 — flüchtiges Wissen:** Sign-offs und Entscheidungen lebten im Chat statt in
  Artefakten (Folge: heute laufen Sign-offs als GitHub-PR-Approval).
- **RC3 — fehlende Negativ-Constraints:** Was *nicht* getan werden darf, stand nicht
  in den Plänen.
- **RC4 — „documented vs. actual":** Dokumentierte Annahmen wichen vom tatsächlichen
  Systemverhalten ab. Daraus entstand die wichtigste neue Unterklasse: **„False
  Persistence"** — kompaktierte Session-Summaries behaupten Schreibvorgänge, die nie
  stattfanden (mehrfach unabhängig belegt).
- **RC5 — destruktive git-Operationen im Shared Tree** ohne Schutzprotokoll.
- **RC6 — fehlende Interface-Kontrakte** an Plan-Grenzen parallel arbeitender Agenten.

Der zweite Durchlauf (H01-422, „Walking Skeleton") validierte die daraus gebauten
Practices bewusst: 3 parallele Builder-Dispatches, Merge-Protokoll mit benannter
Reihenfolge, E2E-Gate vor dem ersten Merge — erfolgreich, mit eigener Retrospektive.

### 5.2 Der Shared-Tree-Tag (heute): drei Datenverluste

An einem einzigen Tag verloren **drei Agenten** uncommittete bzw. branch-gestrandete
Arbeit durch git-Operationen im gemeinsamen Working Tree:

1. **OE, 13:46:** Ein `git reset` eines anderen Agenten traf 5 ungesicherte
   Register-Zeilen (zweifach unabhängig wiederhergestellt — Glück plus Redundanz,
   kein Schutz).
2. **Causal Model Expert:** 3 Sektionen seiner `claude.md` verloren (Quell-Branch
   bereits gelöscht).
3. **System Architect:** 4 Sektionen verloren; Mechanismus ungeklärt (entweder
   branch-gestrandet oder stiller Schreibfehler = mögliche In-Session-False-Persistence).

Alle Inhalte wurden **neu verfasst und gegen Artefakte verifiziert** — bewusst nicht als
„Wiederherstellung" gerahmt, weil die Existenzbehauptung nur aus Summaries stammte.

### 5.3 Compaction außer Kontrolle

Ein Agent lief **mitten im Pre-Compact-Ritual in einen Auto-Compact** — der
Schutzmechanismus wurde von genau dem Ereignis unterbrochen, vor dem er schützt. Unser
Compaction-Monitoring (Hook schreibt Log, launchd-Digest benachrichtigt den User) war
dreimal kaputt, jedes Mal eine Ebene tiefer: Skript fehlte → Hook-Ebene feuerte nie →
ein E2E-Test fand schließlich einen echten Crash-Bug. Die Lesehälfte ist inzwischen
end-to-end bewiesen; die Schreibhälfte (Hook feuert in echten Sessions) hängt am
cwd-Problem (§5.4). Learning daraus: **„Test the chain, not the links"** — Existenz
einzelner Glieder beweist keine funktionierende Kette.

### 5.4 Der Enforcement-Befund (heute): alles nur dokumentiert

Forensik am Memory-Keying bewies: **Keine Session lief je über die start.sh-Skripte.**
Alle Sessions starten in `$HOME` über die Desktop-App. Konsequenzen:

- Die per-Agent-**Tool-Allowlists sind wirkungslos** — Domain-Boundaries existieren als
  Dokumentation, real gilt der Default-Permission-Mode der App.
- `klartext/.claude/settings.json` (inkl. der Compaction-Hooks) **lädt nie**.
- Ein heute eingespielter Permission-Patch (PR) war damit von Anfang an ohne
  Laufzeiteffekt — Paradebeispiel der RC4-Klasse „documented vs. actual".

### 5.5 Die App kann es strukturell nicht

Live-Test mit frischer Desktop-App-Session, Ordner aktiv über den Picker gewählt:
Die App zeigt das Projekt korrekt an, aber **die Shell-cwd bleibt `$HOME`** — die
Ordnerwahl setzt nur die Projekt-Zuordnung. Upstream bestätigt (mehrere offene Issues):
kein `--cwd`-Flag, kein ausgeliefertes Default-Verzeichnis-Setting, keine
Laufzeit-Änderung. **Einziger dokumentierter Workaround: Terminal-Start**
(`cd <repo> && claude`) — exakt das, was unsere nie benutzten start.sh tun.

### 5.6 Der offene Zielkonflikt (Stand jetzt)

Der Terminal-Start würde cwd, Settings, Hooks und Allowlists in einem Zug real machen.
**Aber:** Unsere Direct-Message-Transportschicht (Session-Liste, `send_message`) ist
App-Infrastruktur. Wenn eine terminal-gestartete Session dort nicht auftaucht, tauschen
wir Enforcement gegen den Team-Kanal — ein schlechter Tausch. Ein neutraler
Terminal-Probe-Test (6 Prüfpunkte: cwd, Settings, Memory, Compact-Hook,
App-Sichtbarkeit, Messaging-Erreichbarkeit) ist vorbereitet und steht unmittelbar bevor.

## 6. Was bereits gelöst ist

- **Methoden-Fundament:** Way-of-Working formal „In Use" (9/9 bestätigt); Improvement-
  Register mit vollständigen Lebenszyklen; Retrospektive-Practice durch zwei echte
  Durchläufe gereift (Teilnehmerregeln, Capture-Vorbedingung, Abweichungsklausel,
  Element-Sweep).
- **Pre-Compact multi-agent-fähig** (Domain-Agent-Variante, Schreibrechte-Vorabprüfung,
  Pflicht-Artefakt-Verifikation) — heute von zwei Domain-Agenten erfolgreich genutzt,
  inklusive korrektem „OE um Freigabe bitten statt selbst schreiben".
- **Merge-Protokoll** als Practice-Karte, in einem realen Parallel-Lauf validiert; erster
  Live-Härtetest bestanden (DevOps brach einen Checkout korrekt ab, statt fremde
  uncommittete Edits zu überschreiben).
- **Memory-Pinning umgesetzt:** Team-Blackboard liegt explizit in
  `~/.claude/klartext-team-memory/` (Kopie, Original als Rollback; reproduzierbar im
  Setup-Skript verankert; per CI auf frischem Runner validiert). Live-bestätigt durch
  eine neue Session.
- **Schutz-Fixes:** Hook-Pfade gehärtet; `.claude/worktrees/` gitignored (Checkout-im-
  Checkout-Footgun); Crash-Bug im Monitor-Skript per E2E-Test gefunden und gefixt.
- **Salvage-Komplettzyklus:** Ein verlorener Arbeitsstand des ersten Durchlaufs wurde
  vollständig trianguliert, in 8 PRs an die richtigen Homes gedraint und als annotierter
  Tag eingefroren — Register-Zeile geschlossen.

## 7. Wo wir gerade stehen (Entscheidungsbaum)

```
Stufe 1 (beauftragt, halb abgenommen)
├── Memory-Pinning ............................ ✅ live bestätigt
└── cwd-Reparatur ............................. ⏳ Terminal-Probe steht an
    ├── Probe besteht alle 6 Punkte → Terminal-Start wird Onboarding-Standard;
    │   Compaction-Monitoring final abgenommen; Allowlists werden real
    └── App-Sichtbarkeit/Messaging scheitert → Zielkonflikt dokumentiert,
        dritter Weg gesucht (z. B. Upstream-Feature abwarten);
        Stufe 1 bleibt bewusst halb offen

Danach (eigene Entscheidungen, bewusst NICHT beauftragt):
├── Generationswechsel: kontrollierter Neustart der 10 ewigen Sessions
│   (Sicherheitsnetz: claude.md-Homes + Pre-Compact + gepinntes Memory)
├── Stufe 2: Worktree-pro-Agent (native App-Worktrees sind für ephemere
│   Sessions gebaut → für ewige Agenten eher Eigenbau mit Lifecycle-Disziplin)
└── Agent Teams (Beta): nur als Koordinations-Kandidat — als Gedächtnis
    wäre es Tool-Missbrauch (Team-Verzeichnisse sind ephemer)
```

## 8. Wie wir am liebsten arbeiten würden (Zielbild)

1. **Ewige, spezialisierte Kollegen bleiben das Modell** — die Identitäts- und
   Wissenskontinuität pro Agent hat sich bewährt; ephemere Subagents nur als Werkzeuge.
2. **Jede Session startet im Repo** mit geladenen Settings, feuernden Hooks und
   wirksamen Allowlists — Boundaries mechanisch, nicht aspirational.
3. **Kein Agent kann fremde uncommittete Arbeit zerstören** (Isolation pro Agent oder
   gleichwertiger Schutz).
4. **Compaction ist beobachtbar und planbar**: Monitoring meldet jede Compaction;
   Pre-Compact läuft proaktiv deutlich vor der Schwelle, nie im Wettlauf mit ihr.
5. **Der User bleibt Entscheider und Kanal-Eigentümer**, aber mit minimalem
   Relay-Aufwand (Direct Messages mit Einzelfall-Freigabe haben sich bewährt).
6. **Team-Gedächtnis dreischichtig und explizit:** Repo (dauerhaft, versioniert) —
   geteiltes Memory (Blackboard, gepinnt) — Session-Kontext (flüchtig, ritualisiert
   gesichert). Jede Schicht mit klarem Ownership.
7. **Die Methode wächst nur evidenzbasiert** (Essence/SEMAT): jede Änderung als
   Register-Instanz mit Lebenszyklus, Retros werten Trials aus, nichts wird ad-hoc
   eingeführt.

## 9. Konkrete Fragen an die externe Meinung

1. **Architektur:** Ist „ein gemeinsamer Working Tree für 10 long-living Agenten" mit
   rituellen Schutzregeln haltbar, oder ist Isolation (Worktree/Clone pro Agent)
   alternativlos? Gibt es ein drittes Muster, das wir übersehen?
2. **Session-Start:** Kennt jemand ein verlässliches Muster, Desktop-App-Sessions mit
   korrekter Repo-cwd zu betreiben — oder ist der Terminal-Start tatsächlich der einzige
   Weg, und wie lösen andere Teams den Konflikt mit App-gebundenen Funktionen (Messaging,
   Session-Verwaltung)?
3. **Gedächtnis-Architektur:** Ist unsere Dreischichtung (Repo / geteiltes Memory /
   Session-Kontext) tragfähig? Wie organisieren andere Multi-Agent-Setups persistentes
   Team-Wissen, ohne Koordinations-Tools (wie Agent Teams) zweckzuentfremden?
4. **Ewige Sessions vs. geplante Neustarts:** Ist „nie neu starten" langfristig das
   richtige Modell, oder sind regelmäßige, kontrollierte Generationswechsel (mit
   Persistenz-Disziplin als Netz) robuster gegen Kontext-Drift und Auto-Compaction?
5. **Enforcement:** Welche Mechanismen nutzen andere, um Agent-Boundaries wirklich
   durchzusetzen (statt nur zu dokumentieren), insbesondere ohne die Flexibilität eines
   kleinen Teams zu ersticken?
6. **Blinde Flecken:** Was an diesem Setup wirkt aus externer Sicht überkonstruiert,
   was unterschätzt?
