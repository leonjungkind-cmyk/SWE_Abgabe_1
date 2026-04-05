DROP INDEX IF EXISTS
    kunde.adresse_kunde_id_idx,
    kunde.adresse_plz_idx,
    kunde.bestellung_kunde_id_idx,
    kunde.kunde_nachname_idx;

DROP TABLE IF EXISTS
    kunde.adresse,
    kunde.bestellung,
    kunde.kunde;
