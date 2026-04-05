DROP INDEX IF EXISTS
    adresse_kunde_id_idx,
    adresse_plz_idx,
    bestellung_kunde_id_idx,
    rechnung_kunde_id_idx,
    kunde_nachname_idx;

DROP TABLE IF EXISTS
    adresse,
    bestellung,
    rechnung,
    kunde;

DROP TYPE IF EXISTS
    geschlecht,
    familienstand,
    facharzt;
