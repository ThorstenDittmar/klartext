# 15. Roadmap

Die Implementierung folgt einem Drei-Phasen-Modell mit TDD-Ansatz. Details zu Scope, Stack und Test-Strategie finden sich in Kap. 19.

**Phase 1 – Technischer Durchstich**

Ziel: Technische Machbarkeit beweisen. Alle Kernfunktionalitäten werden mit minimalem Funktionsumfang berührt: Nutzer-Authentifizierung, minimaler Wirkmodell-Editor, Narrativ-Editor, KI-Claim-Extraktion via Claude API, minimaler Transparenzbericht, Leseansicht. Stack: Supabase (PostgreSQL + Auth), FastAPI + Python, React + TypeScript, Vercel.

**Phase 2 – Funktionsfähiger Prototyp**

Ziel: Einen guten Eindruck des Gesamtsystems vermitteln. Vollständige Workflows für alle drei Nutzerrollen, Gateway-Logik, Gegenrede, Recycling, minimale Community, Trust Network. Scope und Stack können durch Erkenntnisse aus Phase 1 angepasst werden.

**Phase 3 – Erste produktionsreife Version**

Ziel: Öffentlich deploybare Version. Performance, Skalierbarkeit, Sicherheit, vollständiger Präsentationsmodus, Admin-Workflows, Mobile-Optimierung, erste öffentliche Beta. Scope wird nach Phase 2 finalisiert.

↗ Querverweis: Vollständige Beschreibung aller drei Phasen, TDD-Ansatz und Stack – vgl. Kap. 19
