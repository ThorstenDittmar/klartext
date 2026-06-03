-- Rename German claim type values in claims.typ to English.
--
-- The ClaimType enum in models/claim.py used German strings as DB values.
-- This aligns them with the English naming convention (CLAUDE.md).
-- The claims table has no CHECK constraint on typ so only data updates
-- are needed.

UPDATE claims SET typ = 'empirical'      WHERE typ = 'empirischer_claim';
UPDATE claims SET typ = 'causal'         WHERE typ = 'kausaler_claim';
UPDATE claims SET typ = 'definitional'   WHERE typ = 'definitorischer_claim';
UPDATE claims SET typ = 'normative'      WHERE typ = 'normativer_claim';
UPDATE claims SET typ = 'prognostic'     WHERE typ = 'prognostischer_claim';
UPDATE claims SET typ = 'counterfactual' WHERE typ = 'kontrafaktischer_claim';
UPDATE claims SET typ = 'methodological' WHERE typ = 'methodischer_claim';
UPDATE claims SET typ = 'uncertainty'    WHERE typ = 'unsicherheitsclaim';
