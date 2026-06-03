# Experiment Scope: Narrative → Claims/Actors → Wirkgefüge

**Datum:** 2026-06-03
**Ziel:** End-to-end Workflow zum Sammeln praktischer Erfahrungen
mit dem Datenmodell. Baut auf bestehender Infrastruktur auf.

---

## Kontext

Bestehend und funktionierend:
- Narrativ-Import (.docx, .md)
- Claim-Extraktion via Claude API
- CausalModel mit Axiomen
- React-Frontend (minimal)

Neu zu bauen in diesem Scope:
- Actor-Extraktion aus Narrativ
- Claims als DocumentAssets mit ClaimStatus
- Actors als DocumentAssets mit ActorType
- Minimales Wirkgefüge (Slot + CausalRelation) aus Claims
- Frontend-Erweiterung für den Workflow

---

## Workflow

```
1. Narrativ hochladen (bestehend)
        ↓
2. Analyse: Claims + Actors extrahieren
        ↓
3. Claims und Actors bestätigen / verwerfen
        ↓
4. Wirkgefüge-Vorschläge aus Claims generieren
        ↓
5. Slots und Relationen bestätigen / anpassen
        ↓
6. CausalModel mit Slots, Relationen und EpistemicStatus speichern
```

---

## Schritt 2: Analyse-Endpunkt

```
POST /narratives/{id}/analyse
```

Ruft Claude API auf mit dem vollständigen Narrativ-Text.
Gibt zurück:

```json
{
  "actors": [
    {
      "label": "Maria Schneider",
      "actor_type": "individual",
      "occurrences": ["Szene 1", "Szene 3"],
      "entity_suggestion": null
    },
    {
      "label": "Zentralbank",
      "actor_type": "institution",
      "occurrences": ["Szene 2"],
      "entity_suggestion": "zentralbank"
    }
  ],
  "claims": [
    {
      "label": "CO₂-Emissionen steigen",
      "text": "Die Emissionen stiegen seit Jahren unaufhörlich.",
      "claim_type": "empirischer_claim",
      "confidence": 0.91,
      "wirkgefuege_suggestion": {
        "type": "slot_zustand",
        "slot": "co2_emissionen",
        "zustand": "steigend"
      }
    },
    {
      "label": "Hohe Emissionen verursachen Temperaturanstieg",
      "text": "...",
      "claim_type": "kausaler_claim",
      "confidence": 0.87,
      "wirkgefuege_suggestion": {
        "type": "causal_relation",
        "source_slot": "co2_emissionen",
        "source_zustand": "hoch",
        "target_slot": "global_temperatur",
        "target_zustand": "steigend",
        "mechanism": "Treibhauseffekt"
      }
    }
  ]
}
```

---

## Schritt 3: Bestätigung

```
POST /narratives/{id}/actors          — Actor anlegen (confirmed)
POST /narratives/{id}/claims          — Claim anlegen (status: DRAFT)
PUT  /narratives/{id}/claims/{id}     — Claim aktualisieren
```

---

## Schritt 4 + 5: Wirkgefüge-Vorschläge

```
POST /narratives/{id}/suggest-wirkgefuege
```

Aggregiert alle DRAFT-Claims des Narrativs und schlägt daraus
ein minimales Wirkgefüge vor:

```json
{
  "suggested_slots": [
    {"identifier": "co2_emissionen", "slot_type": "physical_quantity"},
    {"identifier": "global_temperatur", "slot_type": "physical_quantity"}
  ],
  "suggested_relations": [
    {
      "type": "CausalRelation",
      "source": "co2_emissionen",
      "source_condition": "hoch",
      "target": "global_temperatur",
      "target_effect": "steigend",
      "mechanism": "Treibhauseffekt",
      "epistemic_status": "incomplete"
    }
  ],
  "from_claims": ["claim-uuid-1", "claim-uuid-2"]
}
```

---

## Schritt 6: CausalModel speichern

Bestehende Endpunkte erweitern:

```
POST /causal-models                         — CausalModel anlegen (bestehend)
POST /causal-models/{id}/slots             — Slot hinzufügen (neu)
POST /causal-models/{id}/relations         — CausalRelation hinzufügen (neu)
PUT  /causal-models/{id}/relations/{id}    — Relation aktualisieren (neu)
PUT  /narratives/{id}/causal-model         — Narrativ verknüpfen (bestehend)
POST /claims/{id}/link-to-wirkgefuege      — Claim auf LINKED setzen (neu)
```

---

## Domänenänderungen

### Neue Klassen (Zielarchitektur aus narrative_model.md)

```python
# Actor — DocumentAsset mit asset_type='actor'
Actor:
  id, label, actor_type, entity_ref, notes, audience

# Claim — DocumentAsset mit asset_type='claim'
Claim:
  id, label, text, status, wirkgefuege_ref, confidence, notes, audience

# ClaimStatus
DRAFT / LINKED / UNRESOLVED

# ActorType
individual / organisation / group / institution / abstract_entity
```

### Wirkgefüge-Erweiterungen (aus causal_model.md)

```python
# Slot
Slot:
  id, causal_model_id, identifier, slot_type, epistemic_status

# CausalRelation
CausalRelation:
  id, causal_model_id, identifier,
  source_slot_id, source_condition,
  target_slot_id, target_effect,
  mechanism, epistemic_status
```

### Datenbank

Neue Tabellen:
- `document_assets` (Actor + Claim + andere Assets)
- `document_links` (Verbindungen)
- `slots` (Wirkgefüge-Slots)
- `causal_relations` (Kausalrelationen)

Bestehende Tabellen bleiben erhalten — keine Migration in diesem Scope.

---

## Frontend-Erweiterungen

Bestehende React-Screens erweitern:

1. **Narrativ-Detail:** Button "Analysieren" → startet Schritt 2
2. **Analyse-Ergebnis:** Liste der vorgeschlagenen Actors und Claims
   mit Bestätigen/Verwerfen pro Eintrag
3. **Wirkgefüge-Vorschlag:** Liste der vorgeschlagenen Slots und
   Relationen mit Bearbeiten/Bestätigen
4. **CausalModel-Detail:** Slots und Relationen anzeigen

Kein neues vollständiges UI — Erweiterung des Bestehenden.

---

## Was explizit NICHT in diesem Scope ist

- DocumentNode-Baum (Section, Paragraph, etc.) — Phase 2
- Scope auf Slots und Relationen — Phase 2
- CausalModelFederation / Zeitscheiben — Phase 2
- Vollständige DocumentLink-Navigation — Phase 2
- Migration bestehender Daten — Phase 2
- Community-Features — Phase 2

---

## Erfolgskriterium

Ein Narrativ kann importiert, analysiert und in ein minimales
Wirkgefüge überführt werden. Der Autor sieht welche Claims
welchen Slots und Relationen entsprechen. Ein CausalModel mit
mindestens zwei Slots und einer CausalRelation ist gespeichert
und mit dem Narrativ verknüpft.
