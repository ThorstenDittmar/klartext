# Wirkmodell: Epistemische Transparenz im öffentlichen Diskurs

**Wirkraum:** Öffentlicher politischer und gesellschaftlicher Diskurs in demokratischen Gesellschaften,
Deutschland 2020er Jahre. Medial vermittelter Meinungsaustausch zwischen Bürgerinnen und Bürgern
mit unterschiedlichen Weltbildern.

---

## Axiome

Diese Grundannahmen werden in der Geschichte als gesetzt behandelt – sie sind der Ausgangspunkt,
nicht das Ergebnis der Argumentation.

| ID | Axiom | Typ | Wo in der Geschichte |
|---|---|---|---|
| A1 | Gesellschaftliche Polarisierung entsteht primär durch unsichtbare Annahmen, nicht durch Faktenmangel | empirisch | Szene 2 (Tarek: „Die Annahmen sind unsichtbar...") |
| A2 | Menschen wollen grundsätzlich verstehen – sie wurden nur nie gefragt | normativ/empirisch | Szene 15 (Mara: „Vielleicht wollten die meisten Leute das immer") |
| A3 | Eine Maschine ohne Ego kann Annahmen neutraler markieren als ein Mensch | kausaler_claim | Szene 5 (Tarek: „Weil sie kein Ego hat") |
| A4 | Explizit gemachte Annahmen sind öffentlich verteidigbar und damit diskutierbar | normativ | Szene 8 (Elena: „Die stehen jetzt da. Die kann jeder lesen.") |
| A5 | Narrativer Text ohne explizite Axiome lagert Annahmen in den Leser aus | kausaler_claim | Szene 7 (Priya: „Die Geschichte aktiviert, was schon da ist.") |

---

## Kausalrelationen

```
Unsichtbare Annahmen
    → Scheindiskurse (Streit über Schlussfolgerungen, nicht über Voraussetzungen)
    → Polarisierung
    → Vertrauensverlust in Institutionen und Gesprächspartner

Explizite Annahmen
    → Vergleichbarkeit von Positionen
    → Möglichkeit rationaler Dissensklärung
    → Verständnis für die Perspektive des anderen

Angst vor Veränderung ohne Erklärung (Knut/VW 2019)
    → Selbstdeutung durch Betroffene
    → Suche nach Schuldigen
    → politische Radikalisierung

Narrativ ohne Axiomraum + ausgearbeiteter Wirkraum
    → System kann fehlende Verortung markieren
    → Autor muss Axiomraum explizit machen oder ablehnen
```

---

## Claims der Geschichte

### Kernclaims (explizit ausgesprochen)

| Claim | Sprecher | Szene | Typ |
|---|---|---|---|
| „Nicht die falschen Meinungen. Die unsichtbaren Annahmen dahinter." | Tarek | 2 | kausaler_claim |
| „Vom Prüfer zum Gesprächspartner." | Mara | 5 | definitorischer_claim |
| „Wir prüfen nicht ob jemand recht hat. Wir fragen, ob jemand sagt was er meint." | Elena | 11 | definitorischer_claim |
| „Unbequem und falsch sind nicht dasselbe." | Jonas | 8 | normativer_claim |
| „Das ist kein technisches Problem." | Jonas | 13 | empirischer_claim |

### Implizite Annahmen (vom System zu markieren)

Diese Annahmen stehen **nicht** im Text, sind aber für den Argumentationsgang notwendig:

1. Ein System das Annahmen sichtbar macht, verändert auch das Verhalten der Autoren
   *(belegt durch Bernds zweiten Text und Thomas' Überarbeitung)*

2. Epistemische Transparenz setzt keine Einigkeit voraus – sie ermöglicht konstruktiven Dissens
   *(impliziert durch Jonas' Entwicklung von Ablehnung zu Mitarbeit)*

3. Das Ökosystem der Plattform (Wirkmodell-Autoren + Literaten + Leser) ist notwendig –
   jede Rolle allein reicht nicht
   *(Szene 13: Berufsschullehrer arbeitet korrekt, aber allein)*

---

## Narrative Abweichungen

| Stelle | Abweichung | Typ | Behandlung |
|---|---|---|---|
| Szene 3: Jonas' Ablehnung extremer Positionen | Geschichte setzt voraus dass Demokratiefeindlichkeit erkennbar ist – das ist selbst eine Annahme | implizite_annahme | Offen gelassen – bewusste Spannung |
| Szene 6: Elena's Mutter-Tochter-Szene | Narrativ setzt Unvereinbarkeit von Abhängigkeit und Überzeugung voraus | narrative_abweichung | Vom System erkannt, von Elena akzeptiert und explizit gemacht |
| Szene 7: Bernds axiomfreier Text | Zeigen-statt-Sagen als Strategie umgeht das System | luecke | Führt zur Weiterentwicklung des Systems (Szene 8: „der Schatten") |

---

## Geltungsbereich

- **Zeitlich:** 2022–ca. 2024 (Pandemienachwirkungen, Energiekrise, gesellschaftliche Polarisierung)
- **Räumlich:** Deutschland (Berlin, Zwickau, Leipzig)
- **Sozial:** Gebildete Stadtbevölkerung + Industriearbeiter + Lehrer; bewusst divers gewählt
- **Thematisch:** Öffentlicher Diskurs, epistemische Transparenz, Plattformdesign

---

## Verwendung als Testfall

### Szenen für `POST /extract-claims`

| Szene | Erwartete Claims | Schwierigkeit |
|---|---|---|
| Szene 2 (Tarek erklärt das Problem) | 2–3 kausale Claims, 1 definitorischer | mittel |
| Szene 4 (Wahlprogramm-Test) | 3 Claims direkt benannt | einfach (explizit) |
| Szene 7 (Bernds Text) | 0–1 Claims (axiomfrei!) | schwer – Abwesenheit testen |
| Szene 8 (Bernds zweiter Text) | 3 explizite normative Claims | einfach (explizit) |

### Regressionstest: Szene 7

Bernds erster Text ist ein Grenzfall: **Das System soll wenig finden** – nicht weil der Text gut ist,
sondern weil er keine prüfbaren Aussagen enthält. Das ist ein Indikator für
`Abwesenheit von Axiomen` (Kap. 6.3.2), nicht für Qualität.
