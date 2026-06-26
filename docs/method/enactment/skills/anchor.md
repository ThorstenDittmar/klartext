---
name: anchor
description: >
  Anchor the session — secure everything that only lives in the chat to durable storage BEFORE
  context is lost (via /clear, /compact, or session end). Use whenever the user says "anchor",
  "session sichern", "nichts vergessen", "alles sichern", "vor clear", "vor neustart", "vor compact",
  or anything suggesting they want to checkpoint the session before context is reset. On a RESTART
  (generation change: next step is /clear and a successor session takes over) it also seeds the
  successor. Project-/role-agnostic: all concrete homes, routing, seed mechanism and reading list come
  from the anchor profiles the active CLAUDE.md declares — this skill hardcodes none of them; if no
  profile is declared it asks the user. Supersedes the former `pre-compact` skill — renamed because the
  ritual is no longer tied to /compact (the loss-free path is /clear; /compact only summarizes and is
  False-Persistence-prone).
---

# Anchor — Session Safeguard

Deine Aufgabe: die aktuelle Session systematisch durchgehen, **bevor der Kontext verloren geht** —
durch `/clear` (Generationswechsel, verwirft), `/compact` (fasst zusammen) oder Session-Ende. Ziel:
nichts Wichtiges verlieren — Entscheidungen, Begründungen, mündliche Anweisungen, offene TODOs, der
aktuelle Arbeitsstand. Der Name **anchor**: das flüchtige Chat-Wissen am festen Grund (Platte)
verankern; bei einem Restart zusätzlich einen Anker werfen, an dem die Nachfolge-Session wieder anlegt.

> **Dieser Skill ist der generische Kernel — er kennt KEINE projekt- oder rollen-spezifischen Pfade.**
> Alles Konkrete zieht er aus **deklarierten Anchor-Profilen** (siehe „Profil-Auflösung"). Steht etwas
> Projekt-Spezifisches fest verdrahtet hier drin, ist es ein Bug — melden, nicht befolgen.
>
> **klartext-Enactment:** die konkreten Homes liegen in `docs/method/enactment/anchor-profile.md`
> (Endeavour) + `agents/<rolle>/anchor-profile.md` (Rolle; Domain-Experten teilen
> `docs/method/enactment/anchor-profile.domain-agent.md`). Das jeweilige `agents/<rolle>/claude.md`
> zeigt auf beide. Dieser Repo-Skill ist die SoT, die `klartext skills sync` nach `~/.claude/skills/`
> spiegelt — er bleibt generisch, damit der Sync kein Cross-Projekt-Leck zurückbringt.

## Voraussetzungen — anchor fällt nicht vom Himmel (Bindungen)

Anchor ist eine **Library-Practice mit Außenbindungen**, die gelten müssen, damit das Ritual *wirkt*:
- **`enabled-by` Runtime-Functionalities:** `/clear` (der einzige verlustfreie Pfad) und `/compact`.
  Sie kommen von der Umgebung (Claude-Runtime), sind versionsabhängig — driftet ihre Semantik, bricht
  die Wirksamkeitsannahme.
- **baut auf der Session-Scan-Mechanik auf** (dem Durchsuchen des Verlaufs nach Entscheidungen/
  Begründungen/TODOs). Fehlt sie, fehlt der Motor.
- **liest ein Anchor-Profil**, wenn vorhanden (siehe nächster Abschnitt) — ohne eines arbeitet es mit
  Fallback (universelle Invarianten + Rückfrage).

## Profil-Auflösung (ZUERST) — wie der Kernel projekt-/rollen-spezifisch wird

Das Ritual ist endeavour-agnostisch; jede konkrete Festlegung kommt — wenn deklariert — aus zwei
Tailoring-Schichten:

1. **Endeavour + Rolle bestimmen** — aus dem Arbeitsverzeichnis / dem geladenen `CLAUDE.md` dieser Session.
2. **Die deklarierten Anchor-Profile lesen** (das `CLAUDE.md` zeigt darauf — *Zeiger, nicht Wiederholung*):
   ein **Endeavour-Profil** (gilt für alle Rollen) und ein **Role-Profil** (gilt für die aktive Rolle).
3. **Ein Profil deklariert vier Dinge:**
   - **`storage map`** — wohin welche Wissensart gesichert wird (eigenes Wissen, je Inhaltstyp).
   - **`handoff routing`** — wie Wissen, das einem *anderen* Akteur gehört, das Vorhaben verlässt.
   - **`seed mechanism`** — wie eine Nachfolge-Session geseedet wird (nur Restart).
   - **`reading list`** — was bei jedem Sessionstart neu zu lesen ist.
4. **Kein Profil deklariert / keins vorhanden → FALLBACK:** **frag den User**, wohin gesichert werden soll,
   und arbeite mit den universellen Invarianten unten. **Niemals** projekt-spezifische Pfade *raten* — das
   ist genau der False-Persistence-Fehler (gegen nicht-existente Dateien „sichern"). Ein Nicht-Essence-
   Projekt ohne Profil ist legitim; der Fallback fängt es ab.

## Modus bestimmen (danach)

Kläre — fragen, wenn unklar: ist das ein **Restart** oder ein **Checkpoint**?

- **Restart** (Generationswechsel): als Nächstes kommt `/clear`, eine Nachfolge-Session übernimmt.
  → alle Schritte **inklusive Successor-Seed** (Schritt 4.6).
- **Checkpoint** (mid-session): du sicherst nur zwischendurch und arbeitest danach weiter.
  → Successor-Seed **überspringen** (sonst landen veraltete Handoff-Notizen im Postfach).

## Was einen Kontext-Reset überlebt

**Generisch-invariant** (gilt in jedem Vorhaben): `CLAUDE.md` · Code/Kommentare/Docstrings · Git-Commits ·
GitHub-Issues + TODOs im Code · Skill-Dateien · Memory-Dateien unter `~/.claude/`.

**Profil-spezifisch:** die `storage map` aus dem Endeavour-/Role-Profil. Diese benennt das Profil — nicht
dieser Skill. Ohne Profil: nur die Invarianten + Rückfrage.

**Was verloren gehen kann:** Alles, was nur im Gesprächsverlauf steht. `/clear` *verwirft* es ersatzlos,
`/compact` *fasst es zusammen* (lückenhaft, False-Persistence-Risiko).

## Schritt 1 — Konversation scannen

Lies die gesamte bisherige Konversation. Sammle Kandidaten je Kategorie:
1. **Architektur-Entscheidungen** · 2. **Regeländerungen** (noch nicht durabel) · 3. **Begründungen (Warum)** ·
4. **Mündliche Anweisungen** · 5. **Offene TODOs / nächste Schritte** · 6. **Arbeitsstand** (fertig / in
Arbeit / blockiert) · 7. **Geparkte Befunde** ohne dauerhaftes Zuhause.
Sei großzügig — lieber einen Punkt zu viel als einen übersehen.

## Schritt 1.5 — Routing-/Befund-Check

**Trigger:** nur wenn es echt offene Delegationen / ausgehende Befunde gibt — sonst explizit überspringen.
Durchsuche nach Wissen, das **einem anderen Akteur** gehört (Briefings, Delegationen, Bitten an den User
mit Erwartung an einen anderen Akteur, Befunde außerhalb der eigenen Domäne). Prüfen, ob schon erledigt
(Zieldatei / explizite Bestätigung). Nicht erledigt → über den **im Profil deklarierten `handoff routing`**
weiterreichen (durabler Inbox, falls vorhanden; sonst Briefing an den menschlichen Relay). Welcher
Mechanismus gilt, sagt das Profil — nicht dieser Skill.

## Schritt 2 — Persistenzcheck

Für jeden Punkt: bereits sicher gespeichert (in einer `storage map`-Home, einem Code-Kommentar, einer
Commit-Message, einem Issue, einer Memory-Datei)? Als **bereits gesichert** / **noch nicht gesichert** markieren.

## Schritt 2.5 — Wissens-Routing

Zwei Fragen — beide zählen: **1. Woher kommt das Wissen** (meine Domäne)? **2. Wer hat fachliche Autorität**
darüber? Frage 2 = Expertise/Autorität, nicht Datei-Eigentum. Nennt sie einen anderen Akteur → mindestens
Grenzwissen.

| Typ | Beschreibung | Konsequenz |
|---|---|---|
| **Eigenwissen** | gehört in meine Domäne | → Schritt 3 speichern |
| **Fremdwissen** | gehört ganz einem anderen Akteur | → Briefing über `handoff routing` |
| **Grenzwissen** | betrifft zwei Akteure | → je ein Briefing |
| **Organisationswissen** | Struktur/Zusammenarbeit | → Briefing an den zuständigen Akteur |

**Der Relay ist ein Mensch oder ein deklarierter durabler Inbox — kein Agent schreibt direkt in die Dateien
eines anderen Akteurs.** Welcher konkret gilt, sagt das Profil.

## Schritt 3 — Mit dem User durchgehen

Befunde klar und strukturiert präsentieren, in der Sprache des Users. Erst bestätigen, was schon gesichert
ist und wo. Dann **Block A — Eigenwissen** (je Punkt: sichern? in welche `storage map`-Home? **Schreibrechte
vorher prüfen** — sonst Briefing an den Owner) und **Block B — Briefings** (zeigen, fragen: weiterleiten /
anpassen / überspringen). **Niemals ohne Bestätigung weiterleiten, niemals auto-speichern.** Im Zweifel
**lieber zu viel fragen**.

## Schritt 4 — Bestätigte Punkte speichern + Artefakt-Verifikation

Nach Bestätigung speichern (Edit/Write / Bash für Commits). In bestehende Dateien einfügen — nie überschreiben,
nie duplizieren.

**Pflicht-Abschluss — Artefakt-Verifikation (False-Persistence-Schutz):** nach ALLEN Speicherungen
`git status` / `git diff --stat` (bzw. `ls -la` außerhalb des Repos) ausführen und die tatsächlich geänderten
Dateien gegen die beabsichtigten abgleichen. **Der eigenen Erinnerung oder einer Session-Summary wird NICHT
geglaubt — nur dem Artefakt.** (Beleg: kompaktierte Summaries behaupteten mehrfach Schreibvorgänge, die nie
stattfanden — „False Persistence".)

## Schritt 4.6 — Successor-Seed (NUR im Restart-Modus)

**Überspringen, wenn Checkpoint.** Im Restart: eine Handoff-Notiz über den **im Profil deklarierten
`seed mechanism`** ablegen (Self-Message-Inbox ↔ Reentry-Memory + Checkpoint-Datei — je nach Profil; ohne
Profil: den User fragen, wie geseedet werden soll). Das `CLAUDE.md` lädt die Identität, der Seed liefert den
*Stand*. Inhalt (mechanismus-unabhängig):
- **Stand:** erledigt / in Arbeit / blockiert (mit PR-/Branch-/Commit-Bezügen)
- **Offene Fäden:** nächste Schritte, geparkte Befunde, wartende Briefings
- **Wake-Prompt:** eine konkrete erste Anweisung — eine frische Session handelt nicht von selbst, bevor der
  User die erste Nachricht gibt.

**Artefakt-Verifikation auch hier:** das Seed-Artefakt existiert und ist nicht leer — der Seed ist die
Verlust-Versicherung, er darf nicht selbst dem False-Persistence-Bug zum Opfer fallen.

## Schritt 5 — Kurze Zusammenfassung

Wie viele Punkte gefunden · was war schon gesichert · was neu gesichert · was bewusst übersprungen ·
(Restart) ob der Successor-Seed liegt und verifiziert ist.

## Schritt 6 — Prozess-Verbesserungen

Nur, wenn in der Session etwas Relevantes passiert ist — kein Pflicht-Protokoll. Jeder Kandidat wird über
den **im Profil deklarierten Verbesserungs-Kanal** festgehalten (Register / Parkplatz / Issue), nicht als
loses TODO.

0. **`reading list` vollständig?** Fiel auf, dass ein Dokument **von Anfang an hätte gelesen werden müssen**
   (Wissen, das fehlte und nachgeladen werden musste)? → in die `reading list` des **betroffenen Profils**
   eintragen (Endeavour-Profil, wenn es alle Rollen betrifft; Role-Profil, wenn rollen-spezifisch). So liest
   die nächste Session es ohne Nachfrage.
1. **Neue Skill-Kandidaten?** wiederholte Abfolge, die ein Skill wäre? → beschreiben, der User entscheidet.
2. **Bestehende Skills veraltet?** Hat ein Skill (auch `anchor`) nicht geholfen / Falsches vorgegeben? →
   fixen oder über den Verbesserungs-Kanal festhalten.
3. **Profil aktuell?** Änderte sich, *wo* Wissen hingehört oder *wie* geseedet wird? → betroffenes Profil
   aktualisieren (sofern Schreibrecht; sonst Briefing an den Owner).
4. **GitHub Issues / ADRs vollständig?** TODO ohne Issue? implizit gelöstes Issue offen? Architektur-
   entscheidung, die ein ADR verdient? → anlegen/schließen, wenn der User zustimmt.

---

**Abschluss:** erst nach allen Schritten sagen, dass alles gesichert **und verifiziert** ist. Dann der nächste
Schritt je Modus:
- **Restart:** *„Alles gesichert und verifiziert, Successor-Seed liegt. Du kannst jetzt `/clear` ausführen —
  verlustfreier Generationswechsel: `/clear` verwirft sauber, die Nachfolge bootet aus `CLAUDE.md` + liest
  den Seed."*
- **Checkpoint:** *„Alles gesichert und verifiziert. Du kannst weiterarbeiten."*

**`/clear` und `/compact` NIE selbst ausführen** — warten, bis der User es explizit auslöst.

**`/clear` ist `/compact` vorzuziehen:** `/clear` *verwirft* (zwingt dazu, dass vorher wirklich alles
persistiert wurde — genau dieses Ritual), `/compact` *fasst zusammen* (lückenhaft, False-Persistence-Risiko).
Der Skript hieß früher `pre-compact`; umbenannt zu **anchor**, weil der Name an einen Befehl gebunden war,
der nicht mehr der bevorzugte Weg ist — `anchor` benennt das Wesen (Wissen verankern), nicht den Befehl.
