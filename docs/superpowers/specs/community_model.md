# Community Model — Spezifikation

**Datum:** 2026-06-03
**Status:** Noch nicht in Specs überführt
**Quellen:** Projektskizze V0.25, Kap. 22 und 23

---

## Hinweis

Für das Community Model existieren noch keine technischen Spec-Dateien.
Die konzeptionelle Grundlage liegt in der Projektskizze (Kap. 22–23).
Dieses Dokument fasst den konzeptionellen Stand zusammen und markiert
was noch zu spezifizieren ist.

---

## 1. Zensur-Logik

Drei Kategorien ausgegrauter Inhalte in allen Diskursbereichen:

| Kategorie | Farbe | Schaltbar |
|---|---|---|
| Wahrheitsdebatten | Grau | Ja, per Button |
| Rechtswidrige Inhalte | Andere Farbe | Ja, separat |
| Persönliche Beschimpfungen | Dritte Farbe | Ja, separat |

**Kernprinzip:** Im Community-Bereich darf nur über klar/unklar
gestritten werden, nie über wahr/unwahr. Axiome sind innerhalb des
Systems nicht anfechtbar. Die richtige Antwort auf ein abgelehntes
Axiom ist ein Gegenentwurf, kein Gegenargument.

**Widerspruchsmechanismus:** Administrator (Gutachter) kann
Zensurentscheidungen aufheben. Aufgehobene Zensuren bleiben markiert.

**Verstoß-Tracking:** Drei Zähler pro Nutzer (je Kategorie).
Nutzer entscheidet ob im Profil sichtbar.

---

## 2. Trust Network (EigenTrust+-Analogie)

**Akzeptanz** — nicht Vertrauen, nicht Mögen, nicht Zustimmung.
Neutrale Anerkennung als ernsthafter Diskursteilnehmer.

- Binär: vorhanden oder nicht
- Minimum: 0 (kein Blame-Game, keine negative Markierung)
- Stilles Zurückziehen möglich, keine Benachrichtigung
- Wer akzeptiert wird, sieht nicht wer ihn akzeptiert

**Akzeptanzmuster:** Default privat. Kann vollständig öffentlich
gemacht und abonniert werden. Keine mittlere Stufe.

**Drei Profilwerte:**
1. Persönliche Akzeptanz (eigene Aussage, binär)
2. Peer-Group-Akzeptanz (Mittelwert abonnierter Muster)
3. Systemakzeptanz (Klarname + Betriebsdauer + globaler Mittelwert)

---

## 3. Nutzerprofil

**Öffentlich:** Nutzername, kurze Bio, Systemrollen-Abzeichen
(nur systemvergeben: Admin, Gutachter etc.), drei Akzeptanz-Balken,
optionale Verstoß-Zähler, Werke/Wirkmodelle/Gegenreden/Recyclings,
optionales Akzeptanzmuster, optionale Lesehistorie.

**Nicht-öffentlich:** Klarname, Kontaktinfo (fließt in Systemakzeptanz
ein), vollständige Moderationshistorie.

**Profilansicht eines anderen Nutzers:**
- Persönliches Notizfeld (nur für Betrachter sichtbar)
- Interaktionshistorie (gemeinsame Feedback-, Diskussions-,
  Recycling- und Gegenrede-Berührungspunkte)

---

## 4. Noch zu spezifizieren (Specs fehlen)

| Thema | Priorität |
|---|---|
| User-Domänenmodell (Python-Klassen, DB-Schema) | Hoch |
| Acceptance-Tabelle mit RLS | Hoch |
| Systemakzeptanz als Materialized View | Mittel |
| CommunityPost-Domänenmodell | Mittel |
| Moderationsregeln: Abgrenzung klar/unklar vs. wahr/unwahr | Hoch |
| Verstoß-Tracking-Schema | Mittel |
| Notification-System (3 Abonnementstufen) | Niedrig |
| Spam-/Bot-Schutz im Akzeptanz-System | Niedrig |
| Profildeaktivierung und Account-Löschung | Niedrig |
