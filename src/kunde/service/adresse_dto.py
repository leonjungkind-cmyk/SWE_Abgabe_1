"""DTO für die Adresse, ohne SQLAlchemy-Decorators."""

from dataclasses import dataclass

import strawberry

from kunde.entity.adresse import Adresse

__all__ = ["AdresseDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class AdresseDTO:
    """DTO-Klasse für die Adresse, insbesondere ohne Decorators für SQLAlchemy."""

    plz: str
    ort: str

    def __init__(self, adresse: Adresse) -> None:
        """Initialisierung von AdresseDTO durch ein Entity-Objekt von Adresse.

        :param adresse: Adresse-Objekt mit Decorators für SQLAlchemy
        """
        self.plz = adresse.plz
        self.ort = adresse.ort
