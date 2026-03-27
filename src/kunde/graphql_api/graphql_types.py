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

from kunde.entity import Facharzt, Familienstand, Geschlecht

__all__ = [
    "AdresseInput",
    "CreatePayload",
    "KundeInput",
    "RechnungInput",
    "Suchparameter",
]

# SDL (schema definition language):
# type kunde {
#     nachname: String!
# }
# type Query {
#     kunde(kunde_id: ID!): kunde!
#     kundeen(input: Suchparameter): [kunde!]
# }
# type Mutation {
#     create(kunde_input: KundeInput!): CreatePayload!
# }


@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach Kundeen."""

    nachname: str | None = None
    """Nachname als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""


@strawberry.input
class AdresseInput:
    """Adresse eines neuen Kundeen."""

    plz: str
    """Postleitzahl eines neuen Kundeen."""

    ort: str
    """Ort eines neuen Kundeen."""


@strawberry.input
class RechnungInput:
    """Rechnung zu einem neuen Kundeen."""

    betrag: Decimal
    """Betrag."""

    waehrung: str
    """Währung als 3-stellige Zeichenkette."""


@strawberry.input
class KundeInput:
    """Daten für einen neuen Kundeen."""

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
    """Resultat-Typ, wenn ein neuer kunde angelegt wurde."""

    id: int
    """ID des neu angelegten Kundeen"""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # noqa: N815  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""
