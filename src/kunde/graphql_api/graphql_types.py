"""Strawberry-Typen für die GraphQL-API der Kundenverwaltung."""

import strawberry

__all__ = [
    "AdresseInput",
    "AdresseType",
    "BestellungType",
    "CreatePayload",
    "KundeInput",
    "KundeType",
    "Suchparameter",
]


@strawberry.input
class Suchparameter:
    """Filterkriterien, mit denen Kunden gesucht werden können."""

    nachname: str | None = None
    """Teilstring, nach dem im Nachnamen gefilter wird."""

    email: str | None = None
    """Vollständige Emailadresse, nach der gefiltert wird."""


@strawberry.input
class AdresseInput:
    """Anschrift, die beim Anlegen eines Kunden mitgegeben wird."""

    strasse: str
    """Name der Straße."""

    hausnummer: str
    """Hausnummer inklusive möglichem Zusatz."""

    plz: str
    """Fünfstellige Postleitzahl."""

    ort: str
    """Name der Stadt oder Gemeinde."""


@strawberry.input
class KundeInput:
    """Pflichtfelder, die beim Erstellen eines neuen Kunden übergeben werden."""

    nachname: str
    """Familienname des Kunden."""

    email: str
    """Eindeutige Emailadresse des Kunden."""

    adresse: AdresseInput
    """Wohnanschrift des Kunden."""


@strawberry.type
class AdresseType:
    """Anschrift eines Kunden, wie sie in einer GraphQL-Abfrage zurückgegeben wird."""

    plz: str
    ort: str


@strawberry.type
class BestellungType:
    """Eine einzelne Bestellung, die einem Kunden zugeordnet ist."""

    produktname: str
    menge: int


@strawberry.type
class KundeType:
    """Vollständiger Kundendatensatz als Ergebnis einer GraphQL-Abfrage."""

    id: int | None
    nachname: str
    email: str
    version: int
    adresse: AdresseType
    bestellungen: list[BestellungType]


@strawberry.type
class CreatePayload:
    """Rückgabewert der create-Mutation mit der vergebenen Kunden-ID."""

    id: int
    """Datenbankschlüssel des neu erzeugten Kunden."""
