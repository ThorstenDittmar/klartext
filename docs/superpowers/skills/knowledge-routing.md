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

**Begründung:** Am 2026-06-14 erreichten zwei Kollegen OE nur über den App-Kanal; OEs Inbox war leer,
zwei merge-blockierende Approvals (#110/#111) wären ohne User-Hinweis verpasst worden. „Inbox by choice"
als bloße Konvention hielt nicht — der App-Kanal sickert durch, weil er verfügbar und bequem ist. Daher:
Inbox als verbindlicher Boden, App nur als Klingel darüber.

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
