"""DTO für die Bestellung, ohne SQLAlchemy-Decorators."""

from dataclasses import dataclass

from kunde.entity.bestellung import Bestellung

__all__ = ["BestellungDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class BestellungDTO:
    """Lesbare Repräsentation einer Bestellung ohne direkte Datenbankanbindung."""

    produktname: str
    menge: int

    @classmethod
    def from_bestellung(cls, bestellung: Bestellung) -> "BestellungDTO":
        """Baut ein BestellungDTO aus einer persistierten Bestellung-Entity.

        :param bestellung: Aus der Datenbank geladene Bestellung-Instanz
        :return: Neues BestellungDTO mit den Werten der Bestellung
        :rtype: BestellungDTO
        """
        return cls(produktname=bestellung.produktname, menge=bestellung.menge)
