SET default_tablespace = kundespace;

CREATE TABLE IF NOT EXISTS kunde (
    id        INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1000) PRIMARY KEY,
    nachname  TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS kunde_nachname_idx ON kunde(nachname);

CREATE TABLE IF NOT EXISTS adresse (
    id          INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1000) PRIMARY KEY,
    strasse     TEXT NOT NULL,
    hausnummer  TEXT NOT NULL,
    plz         TEXT NOT NULL CHECK (plz ~ '^\d{5}$'),
    ort         TEXT NOT NULL,
    kunde_id    INTEGER NOT NULL UNIQUE REFERENCES kunde ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS adresse_kunde_id_idx ON adresse(kunde_id);
CREATE INDEX IF NOT EXISTS adresse_plz_idx ON adresse(plz);

CREATE TABLE IF NOT EXISTS bestellung (
    id           INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1000) PRIMARY KEY,
    produktname  TEXT NOT NULL,
    menge        INTEGER NOT NULL CHECK (menge > 0),
    kunde_id     INTEGER NOT NULL REFERENCES kunde ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS bestellung_kunde_id_idx ON bestellung(kunde_id);
