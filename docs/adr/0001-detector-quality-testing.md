# ADR 0001: Inhaltliche Qualitätsprüfung der Detektoren

**Status:** Proposed  
**Datum:** 2026-05-22  
**Autoren:** Thorsten Dittmar

---

## Kontext

klartext.jetzt nutzt KI-gestützte Detektoren, um Texte automatisch zu analysieren. Der erste Detektor ist der **ClaimExtractor**, der Claims (Behauptungen) aus Szenen eines Narrativs extrahiert und epistemisch klassifiziert.

Diese Detektoren können durch automatisierte Unit-Tests auf ihr **technisches Funktionieren** geprüft werden:

- Gibt der Detektor das erwartete Format zurück?
- Werden Fehler korrekt behandelt?
- Schlägt der Detektor bei ungültigen Eingaben fehl?

Was automatisierte Tests **nicht leisten können**: die Prüfung der **inhaltlichen Korrektheit**. Zum Beispiel:

- Extrahiert der ClaimExtractor tatsächlich alle Claims aus einem Text – auch implizite?
- Klassifiziert er kausal vs. normativ korrekt bei ambigen Formulierungen?
- Verhält er sich robust bei verschachtelten Konditionalsätzen oder rhetorischen Fragen?
- Bleibt seine Qualität stabil wenn das zugrundeliegende KI-Modell wechselt?

Diese Fragen können nur von **Domänenexperten** beantwortet werden – Linguisten, Fachexperten für die jeweiligen Rechtsräume und erfahrene Nutzer der Plattform.

---

## Entscheidung

Wir etablieren eine **gesonderte Qualitätssicherungsinfrastruktur** für Detektoren, die von der normalen technischen Testinfrastruktur (pytest, CI) getrennt ist.

### 1. Kuratierte Testkorpora

Für jeden Detektor gibt es ein Testkorpus aus konstruierten Texten:

- Texte sind bewusst gewählt, um **Grenzfälle und verzwickte Formulierungen** abzudecken
- Zu jedem Text gibt es **erwartete Ergebnisse**, die von Experten definiert und validiert wurden
- Das Korpus wächst kontinuierlich – jeder neue Fehlerfall kann als Testfall aufgenommen werden

**Format** (noch zu spezifizieren, siehe [Issue #30](https://github.com/ThorstenDittmar/klartext/issues/30)):

```yaml
# Beispiel-Struktur (vorläufig)
testfall:
  id: claim-extractor-001
  text: "Wäre das Gesetz anders formuliert, hätte es den gewünschten Effekt nicht erzielt."
  erwartete_claims:
    - text: "Das Gesetz hat den gewünschten Effekt nicht erzielt."
      typ: kausaler_claim
      implizit: true
  validiert_von: [linguist-1, expert-2]
  validiert_am: 2026-06-01
```

### 2. Nutzerrolle: Detektor-Kurator

Eine neue Nutzerrolle **Detektor-Kurator** wird eingeführt. Kuratoren:

- Dürfen Testfälle für Detektoren anlegen und bearbeiten
- Bewerten Detektor-Ausgaben auf inhaltliche Korrektheit
- Markieren Detektoren als „validiert" (mit Datum und Modellversion)
- Werden benachrichtigt wenn sich ein Detektor durch ein Modell-Update verändert hat

### 3. Validierungszyklus

Detektoren werden **neu validiert** wenn:

- Das zugrundeliegende KI-Modell wechselt (z.B. Claude Sonnet 4.5 → 4.6)
- Der System-Prompt eines Detektors geändert wird
- Neue Testfälle im Korpus hinzukommen
- Ein Nutzer einen Fehler meldet, der als neuer Testfall aufgenommen wird

### 4. Trennung von technischer CI und inhaltlicher QA

| | Technische Tests (pytest) | Inhaltliche QA (Kuratoren) |
|---|---|---|
| **Ausführung** | Automatisch bei jedem Commit | Manuell, bei Detektor-Änderungen |
| **Prüft** | Format, Fehlerbehandlung, Verhalten | Korrektheit, Robustheit, Qualität |
| **Verantwortlich** | Entwickler | Detektor-Kuratoren (Experten) |
| **Ergebnis** | Grün/Rot | Validierungsbericht mit Datum |

---

## Konsequenzen

**Positiv:**
- Detektoren können inhaltlich validiert werden, unabhängig von technischer Korrektheit
- Modell-Upgrades sind kontrolliert möglich – Qualitätsrückschritte werden erkannt
- Community-Experten können zur Qualität beitragen, ohne Zugang zum Code zu benötigen

**Negativ / offen:**
- Erhöhter Aufwand für Kuratoren – muss durch gute UX kompensiert werden
- Das Format der Testfälle muss noch spezifiziert und implementiert werden
- Die Rolle „Detektor-Kurator" muss ins Rollensystem integriert werden (siehe [Issue #19](https://github.com/ThorstenDittmar/klartext/issues/19))
- Kuratoren müssen rekrutiert und ongeboardet werden

---

## Verwandte Issues

- [#30 – Inhaltliche Qualitätsprüfung der Detektoren](https://github.com/ThorstenDittmar/klartext/issues/30)
- [#19 – Rollensystem und Authentifizierung](https://github.com/ThorstenDittmar/klartext/issues/19)
- [#6 – Konsistenzprüfung axiomatischer Elemente](https://github.com/ThorstenDittmar/klartext/issues/6)
