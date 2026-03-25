-- Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- TEXT statt varchar(n):
-- "There is no performance difference among these three types, apart from a few extra CPU cycles
-- to check the length when storing into a length-constrained column"
-- ggf. CHECK(char_length(nachname) <= 255)

-- https://www.postgresql.org/docs/current/manage-ag-tablespaces.html
SET default_tablespace = patientspace;

-- https://www.postgresql.org/docs/current/sql-createtable.html
-- https://www.postgresql.org/docs/current/datatype.html
-- https://www.postgresql.org/docs/current/sql-createtype.html
-- https://www.postgresql.org/docs/current/datatype-enum.html
CREATE TYPE geschlecht AS ENUM ('MAENNLICH', 'WEIBLICH', 'DIVERS');
CREATE TYPE familienstand AS ENUM ('LEDIG', 'VERHEIRATET', 'GESCHIEDEN', 'VERWITWET');
CREATE TYPE facharzt AS ENUM ('CHIRURGIE', 'HALS_NASEN_OHREN', 'KARDIOLOGIE', 'NEUROLOGIE');

CREATE TABLE IF NOT EXISTS patient (
    id            INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    version       INTEGER NOT NULL DEFAULT 0,
    nachname      TEXT NOT NULL,
                  -- impliziter Index als B-Baum durch UNIQUE
                  -- https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS
    email         TEXT NOT NULL UNIQUE,
                  -- https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS
    kategorie     INTEGER NOT NULL CHECK (kategorie >= 0 AND kategorie <= 9),
                  -- https://www.postgresql.org/docs/current/datatype-boolean.html
    has_newsletter BOOLEAN NOT NULL DEFAULT FALSE,
                  -- https://www.postgresql.org/docs/current/datatype-datetime.html
    geburtsdatum  DATE CHECK (geburtsdatum < current_date),
    homepage      TEXT,
    geschlecht    geschlecht,
    familienstand familienstand,
                  -- https://www.postgresql.org/docs/current/datatype-json.html
                  -- https://www.postgresql.org/docs/current/arrays.html
                  -- fachaerzte    facharzt[],
    fachaerzte    JSONB,
    username      TEXT NOT NULL,
                  -- https://www.postgresql.org/docs/current/datatype-datetime.html
    erzeugt       TIMESTAMP NOT NULL,
    aktualisiert  TIMESTAMP NOT NULL
);

-- default: btree
CREATE INDEX IF NOT EXISTS patient_nachname_idx ON patient(nachname);

CREATE TABLE IF NOT EXISTS adresse (
    id          INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    plz         TEXT NOT NULL CHECK (plz ~ '\d{5}'),
    ort         TEXT NOT NULL,
    patient_id  INTEGER NOT NULL REFERENCES patient ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS adresse_patient_id_idx ON adresse(patient_id);
CREATE INDEX IF NOT EXISTS adresse_plz_idx ON adresse(plz);

CREATE TABLE IF NOT EXISTS rechnung (
    id          INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
                -- https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-NUMERIC-DECIMAL
                -- https://www.postgresql.org/docs/current/datatype-money.html
                -- 10 Stellen, davon 2 Nachkommastellen
    betrag      NUMERIC(10,2) NOT NULL,
    waehrung    TEXT NOT NULL CHECK (waehrung ~ '[A-Z]{3}'),
    patient_id  INTEGER NOT NULL REFERENCES patient ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS rechnung_patient_id_idx ON rechnung(patient_id);
