# Task Readiness — Bereitschafts-Protokoll

Diesen Skill aufrufen wenn du von Hannibal einen Task dispatcht bekommst,
bevor du mit der Umsetzung beginnst.

Ziel: sicherstellen dass alle Voraussetzungen erfüllt sind bevor Code geschrieben wird.
Lieber 5 Minuten früher klären als nachher zurückrudern.

---

## Schritt 1 — Infos vollständig?

Lies den Task-Beschrieb im Umsetzungsplan sorgfältig:

- [ ] Ist der Scope klar — was gehört dazu, was nicht?
- [ ] Sind alle Dateipfade die ich bearbeiten soll benannt?
- [ ] Gibt es ein konkretes Check-Kommando als DOD?
- [ ] Sind Abhängigkeiten zu anderen Tasks geklärt (Dependency-Kette)?

**Wenn nein:** Hannibal fragen bevor du beginnst.

---

## Schritt 2 — QA-Checkpoint

Bevor du eine einzige Zeile schreibst:

- [ ] Sind die DODs prüfbar? ("Tests grün" ist keine DOD — `klartext test` läuft grün ist eine.)
- [ ] Ist das Fake-Contract für meine Abhängigkeiten aktuell?
  (Wenn du ein Repository-Interface änderst: QA-Briefing vor dem Start)
- [ ] Welche Testschichten erwartet QA für neue Source-Dateien?
  (Domain / Service / Repository / Router — QA hat das in der Koordinationsrunde festgelegt)

**Wenn Fake-Contract veraltet oder unklar:** QA briefen, warten bis Fake aktuell ist.

---

## Schritt 3 — Koordinationsbedarf?

- [ ] Brauche ich Input von einem anderen Agent um zu beginnen?
- [ ] Ändere ich etwas das einen anderen Agent betrifft? (Briefing formulieren)
- [ ] Gibt es Dateipfad-Überlappungen mit einem parallel laufenden Task?

**Wenn Überlappung erkannt:** Hannibal informieren. Nicht einfach beginnen.

---

## Schritt 4 — SA-Eskalation nötig?

- [ ] Entsteht durch meinen Task ein neues Layer-Crossing?
- [ ] Muss ich eine Domain-Grenze überqueren?
- [ ] Entsteht eine Schnittstelle zu einem anderen Domain?

**Wenn ja:** SA eskalieren via Hannibal — nicht selbst entscheiden.
Die Modell-Grenz-Regel gilt: keine cross-domain Schnittstelle ohne SA-Zustimmung.

---

## Schritt 5 — Los

Alle Checks grün? Dann:

1. **Tests zuerst** — `tdd` Skill aufrufen
2. **Branch anlegen** — Schema: `task/<H-id>/<slug>`
3. Umsetzung
4. PR öffnen (kein direkter Push auf `main`)
5. Nach fremden Merges auf `main` rebasieren

Wenn ein anderer Task auf `main` gemergt wurde während du arbeitest:
`git rebase main` — nicht warten bis zum eigenen PR.

---

## Roundup melden

Wenn dein PR gemergt ist: Hannibal informieren.
Hannibal koordiniert den QA-Gate — du bist fertig wenn QA grünes Licht gibt.
