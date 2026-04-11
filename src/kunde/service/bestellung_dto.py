"""DTO für die Bestellung, ohne SQLAlchemy-Decorators."""

from dataclasses import dataclass

import strawberry

from kunde.entity.bestellung import Bestellung

__all__ = ["BestellungDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class BestellungDTO:
    """DTO-Klasse für die Bestellung, insbesondere ohne Decorators für SQLAlchemy."""

    produktname: str
    menge: int

    def __init__(self, bestellung: Bestellung) -> None:
        """Initialisierung von BestellungDTO durch ein Entity-Objekt von Bestellung.

        :param bestellung: Bestellung-Objekt mit Decorators für SQLAlchemy
        """
        self.produktname = bestellung.produktname
        self.menge = bestellung.menge
