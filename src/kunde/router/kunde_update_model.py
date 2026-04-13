"""Pydantic-Model zum Aktualisieren von Kundedaten."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr

from kunde.entity import Kunde

__all__ = ["KundeUpdateModel"]


class KundeUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Kundedaten."""

    nachname: str
    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nachname": "Test",
                "email": "test@acme.com",
            },
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Konvertierung der primitiven Attribute in ein Dictionary.

        :return: Dictionary mit den Attributen für Kunde
        :rtype: dict[str, Any]
        """
        kunde_dict = self.model_dump()
        kunde_dict["id"] = None
        kunde_dict["adresse"] = None
        kunde_dict["bestellungen"] = []
        kunde_dict["username"] = None
        return kunde_dict

    def to_kunde(self) -> Kunde:
        """Konvertierung in ein Kunde-Objekt für SQLAlchemy.

        :return: Kunde-Objekt für SQLAlchemy
        :rtype: Kunde
        """
        logger.debug("self={}", self)
        kunde_dict = self.to_dict()
        kunde = Kunde(**kunde_dict)
        logger.debug("kunde={}", kunde)
        return kunde
