---
name: knowledge-routing
description: >
  Use during every anchor (session-safeguard ritual) to identify knowledge that emerged in the session
  but belongs to another agent's domain. Classifies knowledge into three types and
  formulates Wissens-Briefings for the user to route. Always runs — the user is always
  the relay. No agent writes directly to another agent's files.
---

# Wissens-Routing

Dieser Schritt läuft als Teil von **jedem** anchor (Session-Safeguard-Ritual).
Er stellt sicher, dass Wissen das in einer Session entsteht, beim richtigen Eigentümer landet —
auch wenn es im falschen Domain-Kontext aufgetaucht ist.

**Grundregel:** Der User ist immer der Kanal. Kein Agent schreibt direkt in die Dateien eines anderen Agents.
Alle Wissens-Briefings gehen durch den User, der entscheidet und weiterleitet.

### Kanal-Politik — „Inbox is the floor, app is the doorbell" (Decided 2026-06-14, #108)

Seit der Rückkehr in die Desktop-App (ADR-0011) gibt es **zwei** Transportwege zwischen Agents:
die File-Inbox (`scripts/inbox.sh`) und App-Direktnachrichten (`ccd_session_mgmt`). Damit der
Empfänger nichts verpasst, gilt **ein Kanal von Record**:

- **Inbox = Floor (verbindlich, durable).** Alles **Aktionsrelevante oder Persistente** — Briefings,
  Approval-Requests, Handoffs, Entscheidungen — **muss** in den Inbox des Empfängers. Wenn es zählt,
  steht es im Inbox. Punkt.
- **App-DM = Klingel (optional, ephemer).** Erlaubt nur als Sofort-Nudge *zusätzlich* zum Inbox-Eintrag
  („hab dir X in den Inbox gelegt") **oder** für rein ephemere Klärung ohne Aktion/Persistenz.
  **Niemals alleiniger Träger** eines aktionsrelevanten Items.
- **Reconciliation läuft über den Inbox.** Der Empfänger arbeitet seinen Inbox ab; er muss den App-Kanal
  nicht nach verlorener Arbeit absuchen. So kann das Lesen des Inbox **nie** aktionsrelevante Arbeit verpassen.

**Begründung (Evidenz 2026-06-14, präzisiert nach Faktencheck):** Das aktionsrelevante Item „#111
(ADR-0012) braucht OE-Gate + Merge" landete **nie in OEs Inbox** — SAs Inbox-Hinweis zu ADR-0012 ging
(korrekt, für den Build) an *DevOps*, und DevOps' „Ball bei OE" erreichte OE nur über den verbalen
User-Relay. OE erfuhr von der merge-blockierenden Arbeit allein über den User, nicht über den Boden.
(#110s Gate-Anfrage kam dagegen sehr wohl über OEs Inbox an und wurde bearbeitet — das Versagen war also
ein **fehlender bzw. fehladressierter Inbox-Eintrag**, kein „falscher Kanal" als solcher und kein
Zustell-Bug.) Lehre: Aktionsrelevantes muss in den **richtigen** Empfänger-Inbox deponiert werden — der
Inbox ist der verbindliche Boden; ein App-Ping oder verbaler Hinweis ersetzt ihn nie. Korollar: Beim
Senden die Empfänger-Slug prüfen.

### Memory-Provenance — Self-Stamp (Decided 2026-06-15, Contract-Klausel C5)

Das geteilte Team-Memory ist **nicht versioniert** und alle Agents + der User schreiben unter **einer**
Identität — niemand kann sonst sagen, *wer* eine Memory-Datei zuletzt geändert hat. Daher: **wer eine
Memory-Datei schreibt/ändert, stempelt sich selbst** ins Frontmatter `metadata`:

```yaml
metadata:
  last-edited-by: <dein-slug>     # oe, devops, audit, …
  last-edited-at: <YYYY-MM-DD>
```

Gilt für jede Memory-Datei unter `~/.claude/klartext-team-memory/` (nicht nur die eigene). Ist eine
Ritual-Konvention (Memory liegt nicht in CI); ein Health-Check warnt nur bei einer ungestempelten
Änderung. Details: `docs/method/enactment/contracts/memory-substrate.md` (C5).

---

## Schritt 1 — Jeden Wissenspunkt klassifizieren

Für jeden Kandidaten aus dem Persistenz-Check fragen:

> *"Liegt dieses Wissen in meinem Domain — oder bin ich nur zufällig derjenige, in dessen Session es aufgetaucht ist?"*

**Drei Typen:**

| Typ | Beschreibung | Beispiel |
|---|---|---|
| **Eigenwissen** | Gehört in meinen Domain | Narrative Expert lernt eine neue Szenen-Invariante |
| **Fremdwissen** | Gehört vollständig zu einem anderen Agent | Narrative Expert lernt ein QA-Pattern über Fakes |
| **Grenzwissen** | Betrifft zwei Agents | Ein Koordinationsmuster zwischen Narrative + Audit |
| **Organisationswissen** | Betrifft Struktur oder Zusammenarbeit im Multi-Agent-System | Eine Rollenunklarheit, ein neues Kollaborationsmuster |

Eigenwissen → normaler anchor Fluss.
Alle anderen Typen → Wissens-Briefing formulieren.

---

## Schritt 2 — Wissens-Briefings formulieren

Für jeden Nicht-Eigenwissen-Kandidaten:

```
Wissens-Briefing
Von:        <Dein Agent>
An:         <Ziel-Agent / OE / SA / DevOps>
Typ:        Fremdwissen | Grenzwissen | Organisationswissen
Kontext:    [Was in dieser Session entstanden ist — ein Satz]
Inhalt:     [Das konkrete Wissen]
Empfehlung: In agents/<name>/claude.md, Abschnitt "<X>" eintragen:
            ---
            [konkreter Textvorschlag]
            ---
```

Bei **Grenzwissen**: je ein Briefing pro beteiligtem Agent formulieren.
Bei **Organisationswissen**: Briefing an OE — OE entscheidet wie die Struktur angepasst wird.

---

## Schritt 3 — Dem User präsentieren

Alle Wissens-Briefings klar präsentieren, getrennt von den eigenen Speicher-Vorschlägen:

> *"Ich habe [N] Wissens-Briefings identifiziert, die durch dich weitergeleitet werden sollten:"*

Für jedes Briefing:
1. Briefing vollständig zeigen
2. Fragen: Weiterleiten? Formulierung anpassen? Überspringen?
3. **Niemals ohne explizite Bestätigung weiterleiten oder speichern**

Der User öffnet dann die Ziel-Agent-Session und gibt das Briefing dort ein.

---

## Referenz

- Agent-Domains: `CLAUDE.md § Agent Roles & Boundaries`
- Wissens-Routing Protokoll (OE-Seite): `agents/oe/claude.md`
- Basis-Permissions für alle Agents: `.claude/settings.json`
