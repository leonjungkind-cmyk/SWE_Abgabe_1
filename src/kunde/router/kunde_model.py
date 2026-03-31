"""Pydantic-Model für Kundendaten."""

from typing import Final

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr

from kunde.entity import Kunde
from kunde.router.adresse_model import AdresseModel

__all__ = ["KundeModel"]


class KundeModel(BaseModel):
    """Pydantic-Model für einen Kunden (Create-Request)."""

    nachname: str
    """Nachname."""

    email: EmailStr
    """E-Mail-Adresse."""

    adresse: AdresseModel
    """Adresse."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nachname": "Müller",
                "email": "mueller@example.de",
                "adresse": {
                    "strasse": "Hauptstraße",
                    "hausnummer": "12",
                    "plz": "76133",
                    "ort": "Karlsruhe",
                },
            },
        }
    )

    def to_kunde(self) -> Kunde:
        """Konvertierung in ein Kunde-Objekt.

        :return: Kunde-Entity
        :rtype: Kunde
        """
        logger.debug("self={}", self)

        adresse = self.adresse.to_adresse()

        kunde: Final = Kunde(
            id=None,
            nachname=self.nachname,
            email=str(self.email),
            adresse=adresse,
            bestellungen=[],
        )

        logger.debug("kunde={}", kunde)
        return kunde
