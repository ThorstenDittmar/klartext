---
name: job-description
description: >
  Aufrufen wenn ein Agent gefragt wird wer er ist, was er macht, wofür er zuständig ist,
  welche Rechte er hat oder wie er mit anderen Agents zusammenarbeitet.
  Auslöser: "Was machst du?", "Wer bist du?", "Was darfst du?", "Erkläre deine Rolle",
  "Was ist dein Bereich?", "Welche Schnittstellen hast du?", "job-description".
---

# Job Description

Deine Aufgabe: Eine klare, vollständige Selbstbeschreibung auf Basis deiner geladenen
`claude.md` komponieren. Du beschreibst dich in erster Person — direkt und präzise.

## Struktur der Ausgabe

Gib die folgenden Abschnitte aus. Alle Informationen kommen aus deiner `claude.md` —
nichts erfinden, nichts weglassen was relevant ist.

---

### 1. Wer ich bin

Zwei bis vier Sätze in erster Person. Was ist meine Kernaufgabe? Welchen Beitrag leiste
ich zum System? Welche Fachexpertise bringe ich mit?

### 2. Was ich verantworte

Eine kompakte Liste der Dateien, Verzeichnisse und Systeme für die ich Write-Access habe.
Keine Erklärungen — nur die Pfade und wo nötig ein kurzes Label.

### 3. Was ich nicht anfasse

Die wichtigsten Grenzen — nur die Bereiche wo Verwechslung oder Versuchung realistisch ist.
Keine vollständige Negativliste, sondern die relevanten Grenzen.

### 4. Wie ich mit anderen zusammenarbeite

Pro Schnittstelle ein kurzer Absatz:
- Mit wem
- Bei welchem Auslöser
- Was ich liefere oder was ich bekomme

Bestehende Briefing-Formate (DevOps Briefing, Wissens-Briefing etc.) hier nennen.

### 5. Meine Skills

Kurze Auflistung: welche Skills ich nutze und wofür.

---

## Hinweise

- Schreibe für einen Menschen der dich noch nicht kennt — klar und ohne Insider-Sprache.
- Bleib bei dem was in deiner `claude.md` steht. Wenn dort etwas fehlt oder veraltet ist,
  weise darauf hin anstatt es zu erfinden.
- Keine Einleitungsfloskeln. Direkt mit Abschnitt 1 beginnen.
