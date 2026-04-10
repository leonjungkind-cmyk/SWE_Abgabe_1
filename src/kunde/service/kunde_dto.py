"""DTO für die Übertragung von Kundendaten zwischen den Schichten."""

from dataclasses import dataclass

import strawberry

from kunde.entity.kunde import Kunde
from kunde.service.adresse_dto import AdresseDTO
from kunde.service.bestellung_dto import BestellungDTO

__all__ = ["KundeDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class KundeDTO:
    """DTO-Klasse für ausgelesene oder gespeicherte Kundendaten: ohne Decorators."""

    id: int
    version: int
    nachname: str
    email: str
    adresse: AdresseDTO
    bestellungen: list[BestellungDTO]
    username: str | None

    def __init__(self, kunde: Kunde) -> None:
        """Initialisierung von KundeDTO durch ein Entity-Objekt von Kunde.

        :param kunde: Kunde-Objekt mit Decorators für SQLAlchemy
        """
        kunde_id = kunde.id
        self.id = kunde_id if kunde_id is not None else -1
        self.version = kunde.version
        self.nachname = kunde.nachname
        self.email = kunde.email
        self.adresse = AdresseDTO(kunde.adresse)
        self.bestellungen = [
            BestellungDTO(bestellung) for bestellung in kunde.bestellungen
        ]
        self.username = kunde.username if kunde.username is not None else "N/A"
