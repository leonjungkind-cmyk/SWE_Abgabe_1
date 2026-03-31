"""Pydantic-Model für die Adresse eines Kunden."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from kunde.entity import Adresse

__all__ = ["AdresseModel"]


class AdresseModel(BaseModel):
    """Pydantic-Model für die Adresse eines Kunden."""

    strasse: Annotated[str, StringConstraints(max_length=64)]
    """Straße."""

    hausnummer: Annotated[str, StringConstraints(max_length=10)]
    """Hausnummer."""

    plz: Annotated[str, StringConstraints(pattern=r"^\d{5}$")]
    """Postleitzahl."""

    ort: Annotated[str, StringConstraints(max_length=64)]
    """Ort."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "strasse": "Hauptstraße",
                "hausnummer": "12",
                "plz": "76133",
                "ort": "Karlsruhe",
            },
        }
    )

    def to_adresse(self) -> Adresse:
        """Konvertiert das Modell in eine Adresse-Entity.

        :return: Adresse-Objekt für SQLAlchemy
        :rtype: Adresse
        """
        adresse_dict = self.model_dump()
        adresse_dict["id"] = None
        adresse_dict["kunde_id"] = None
        adresse_dict["kunde"] = None

        return Adresse(**adresse_dict)
