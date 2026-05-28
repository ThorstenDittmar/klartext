-- narrative_akteure: Akteure eines Narrativs (Figuren, Organisationen, Gruppen etc.)
--
-- Akteure sind die handelnden oder betroffenen Entitäten innerhalb eines Narrativs.
-- Sie bilden die Verbindung zum Wirkmodell: ein Akteur kann auf eine Entität (Typ C)
-- im verknüpften Wirkmodell gemappt werden.

CREATE TABLE narrative_akteure (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narrativ_id UUID NOT NULL REFERENCES narrative(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    typ         TEXT NOT NULL
                    CHECK (typ IN (
                        'figur', 'organisation', 'gruppe',
                        'institution', 'abstrakte_entitaet'
                    )),
    beschreibung TEXT DEFAULT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_akteure_narrativ ON narrative_akteure(narrativ_id);
