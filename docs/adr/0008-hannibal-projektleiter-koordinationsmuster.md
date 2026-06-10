# 0008 — Hannibal: Projektleiter und Koordinationsmuster

**Status:** Proposed

## Kontext

Bisher koordinieren Agents im klartext Multi-Agent-System ausschließlich bilateral:
Agent A schickt ein Briefing an Agent B, der User entscheidet ob er es weiterleitet.
Dieses Muster skaliert nicht wenn große Arbeitspakete mehrere Agents gleichzeitig
betreffen — es gibt niemanden der die Gesamtsicht hat, Abhängigkeiten erkennt und
sicherstellt dass alle Teilaufgaben in der richtigen Reihenfolge abgearbeitet werden.

Der User muss heute Arbeitspakete selbst in Einzelaufgaben schneiden, die Reihenfolge
festlegen und sicherstellen dass alle Agents koordiniert sind. Das gehört nicht zum
User — das ist Projektleitungsarbeit.

## Entscheidung

Wir führen einen zehnten Agent ein: **Hannibal** (Projektleiter). Er empfängt große
Arbeitspakete vom User, plant sie, koordiniert alle betroffenen Agents und überwacht
die Umsetzung bis zum QA-Gate im Roundup.

**Kernprinzipien des Koordinationsmusters:**

1. **Zentralisierter Planer, dezentrale Ausführung.** Hannibal plant und koordiniert,
   die Domain-Agents führen aus. Hannibal schreibt keinen Code, deployed nicht und führt
   keine operativen Tätigkeiten durch.

2. **Zweistufiger Abstimmungsprozess.** Erst inhaltliche Abstimmung mit User (Scope,
   grobe Zuständigkeiten), dann Koordinationsrunde mit allen betroffenen Agents. Erst
   danach entsteht der Umsetzungsplan.

3. **User gibt frei, Hannibal dispatcht.** Nach Freigabe des Plans dispatcht Hannibal
   selbst — der User ist nicht der Kanal für den Dispatch.

4. **SA-Eskalation vor dem Dispatch, nicht danach.** Wenn ein Arbeitspaket
   Domain-Grenzen überquert, muss SA zustimmen bevor Hannibal dispatcht. Die
   Modell-Grenz-Regel gilt auch für Hannibal.

5. **QA als Kriterien-Eigentümer in der Koordinationsrunde.** QA legt fest welche
   Testschichten für jede neue Source-Datei erwartet werden — nicht im Roundup,
   sondern vor dem Dispatch.

6. **Maschinell prüfbare DODs.** Jedes TODO im Umsetzungsplan hat ein konkretes
   Check-Kommando als Definition of Done.

7. **Bereitschafts-Protokoll für alle Agents.** Jeder dispatche Agent prüft vor
   der Umsetzung: Infos vollständig? DODs prüfbar? Fake-Contract aktuell?
   Koordinationsbedarf? SA-Eskalation nötig? (→ `task-readiness` Skill)

8. **Struktureller QA-Gate im Roundup.** Kein narrativer Abschlussbericht —
   Hannibal triggert QA, QA gibt grünes Licht oder blockiert.

**Branch & Code-Management:**
- Schema: `task/<H-id>/<slug>` — ein Branch pro Aufgabe, kurzlebig
- PR-basierte Integration — kein direkter Push auf `main`
- Niemals parallele Agents auf denselben Dateipfaden
- Repository-Interface-Änderungen immer sequenziell (Fake-Contract-Risiko)

**Technische Grenze statt Policy:**
Hannibals `start.sh` gewährt keinen Write-Access auf `api/`, `frontend/`,
`.github/` oder andere operative Bereiche. Die Grenze ist technisch erzwungen.

## Konsequenzen

**Positiv:**
- User gibt Arbeitspakete ab, nicht Einzelaufgaben
- Hannibal hat die Gesamtsicht und erkennt Abhängigkeiten früh
- Koordinationsprobleme werden in der Planungsphase aufgedeckt, nicht im Roundup
- Klare Verantwortlichkeit: ein Agent ist für den Gesamtfortschritt zuständig

**Negativ / Risiken:**
- Hannibal ist ein Single Point of Failure bei der Planung
- Die Grenze zwischen "Zuständigkeiten koordinieren" und "fachlich entscheiden"
  ist dünn — Hannibal muss bei Architektur-Fragen konsequent an SA eskalieren
- Das multilaterale Konsultationsmuster (Hannibal fragt mehrere Agents gleichzeitig)
  ist neu und noch nicht erprobt; bilaterale Koordination zwischen Agents bleibt
  weiterhin der Standard für alles was nicht durch Hannibal koordiniert wird

**Offene Fragen:**
- Wie wird Hannibals Koordinationsrunde technisch abgewickelt? (Sub-Agents, sequenziell?)
- Wie granular sollten Arbeitspakete sein? (Tagesarbeit? Wochenarbeit?)

**ADR in Kraft wenn:** SA gibt `Accepted` nachdem die Modell-Grenz-Frage im
Workflow explizit verankert ist (SA-Eskalation als fester Schritt 2).
