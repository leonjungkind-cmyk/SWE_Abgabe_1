# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Schema für GraphQL."""

from datetime import date
from decimal import Decimal

import strawberry

from patient.entity import Facharzt, Familienstand, Geschlecht

__all__ = [
    "AdresseInput",
    "CreatePayload",
    "PatientInput",
    "RechnungInput",
    "Suchparameter",
]

# SDL (schema definition language):
# type Patient {
#     nachname: String!
# }
# type Query {
#     patient(patient_id: ID!): Patient!
#     patienten(input: Suchparameter): [Patient!]
# }
# type Mutation {
#     create(patient_input: PatientInput!): CreatePayload!
# }


@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach Patienten."""

    nachname: str | None = None
    """Nachname als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""


@strawberry.input
class AdresseInput:
    """Adresse eines neuen Patienten."""

    plz: str
    """Postleitzahl eines neuen Patienten."""

    ort: str
    """Ort eines neuen Patienten."""


@strawberry.input
class RechnungInput:
    """Rechnung zu einem neuen Patienten."""

    betrag: Decimal
    """Betrag."""

    waehrung: str
    """Währung als 3-stellige Zeichenkette."""


@strawberry.input
class PatientInput:
    """Daten für einen neuen Patienten."""

    nachname: str
    """Nachname."""

    email: str
    """Emailadresse."""

    kategorie: int
    """Kategorie."""

    has_newsletter: bool
    """Angabe, ob der Newsletter abonniert ist."""

    geburtsdatum: date
    """Geburtsdatum."""

    familienstand: Familienstand
    """Familienstand."""

    homepage: str | None
    """Optionale Homepage."""

    geschlecht: Geschlecht
    """Geschlecht."""

    adresse: AdresseInput
    """Adresse."""

    rechnungen: list[RechnungInput]
    """Rechnungen."""

    fachaerzte: list[Facharzt]
    """Fachärzte."""

    username: str
    """Benutzername."""


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer Patient angelegt wurde."""

    id: int
    """ID des neu angelegten Patienten"""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # noqa: N815  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""
