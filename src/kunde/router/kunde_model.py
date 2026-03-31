"""Pydantic-Model für Kundendaten."""

from loguru import logger

from kunde.entity import Kunde
from kunde.router.adresse_model import AdresseModel

__all__ = ["KundeModel"]


class KundeModel:
    """Pydantic-Model für einen Kunden (Create-Request)."""

    nachname: str
    """Nachname."""

    email: str
    """E-Mail-Adresse."""

    adresse: AdresseModel
    """Adresse."""

    def to_kunde(self) -> Kunde:
        """Konvertierung in ein Kunde-Objekt.

        :return: Kunde-Entity
        :rtype: Kunde
        """
        logger.debug("self={}", self)

        kunde = Kunde(
            nachname=self.nachname,
            email=self.email,
        )

        kunde.adresse = self.adresse.to_adresse()

        logger.debug("kunde={}", kunde)
        return kunde
