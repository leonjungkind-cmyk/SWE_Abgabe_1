"""DTO für die Adresse, ohne SQLAlchemy-Decorators."""

from dataclasses import dataclass

from kunde.entity.adresse import Adresse

__all__ = ["AdresseDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class AdresseDTO:
    """Lesbare Repräsentation einer Adresse ohne direkte Datenbankanbindung."""

    plz: str
    ort: str

    @classmethod
    def from_adresse(cls, adresse: Adresse) -> "AdresseDTO":
        """Baut ein AdresseDTO aus einer persistierten Adresse-Entity.

        :param adresse: Aus der Datenbank geladene Adresse-Instanz
        :return: Neues AdresseDTO mit den Werten der Adresse
        :rtype: AdresseDTO
        """
        return cls(plz=adresse.plz, ort=adresse.ort)
