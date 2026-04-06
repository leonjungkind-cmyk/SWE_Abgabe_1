"""DTO für die Übertragung von Kundendaten zwischen den Schichten."""

from __future__ import annotations

from dataclasses import dataclass

from kunde.entity.kunde import Kunde
from kunde.service.adresse_dto import AdresseDTO
from kunde.service.bestellung_dto import BestellungDTO

__all__ = ["KundeDTO"]


@dataclass
class KundeDTO:
    """Lesbare Repräsentation eines Kunden ohne direkte Datenbankanbindung."""

    id: int | None
    nachname: str
    email: str
    version: int
    adresse: AdresseDTO
    bestellungen: list[BestellungDTO]

    @classmethod
    def from_kunde(cls, kunde: Kunde) -> KundeDTO:
        """Baut ein KundeDTO aus einer persistierten Kunde-Entity.

        :param kunde: Aus der Datenbank geladene Kunde-Instanz
        :return: Neues KundeDTO mit den Werten des Kunden
        :rtype: KundeDTO
        """
        return cls(
            id=kunde.id,
            nachname=kunde.nachname,
            email=kunde.email,
            version=kunde.version,
            adresse=AdresseDTO.from_adresse(kunde.adresse),
            bestellungen=[
                BestellungDTO.from_bestellung(b) for b in kunde.bestellungen
            ],
        )
