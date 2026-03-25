# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Pydantic-Model zum Aktualisieren von Patientendaten."""

from datetime import date
from typing import Annotated, Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, StringConstraints

from patient.entity.familienstand import Familienstand
from patient.entity.geschlecht import Geschlecht
from patient.entity.patient import Patient

__all__ = ["PatientUpdateModel"]


class PatientUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Patientendaten."""

    # https://docs.pydantic.dev/latest/usage/types
    nachname: Annotated[
        str,
        StringConstraints(
            pattern="^[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß])?$",
            max_length=64,
        ),
    ]
    """Der Nachname."""
    email: EmailStr
    """Die eindeutige Emailadresse."""
    kategorie: Annotated[int, Field(ge=1, le=9)]
    """Die Kategorie."""
    has_newsletter: bool
    """Angabe, ob der Newsletter abonniert ist."""
    geburtsdatum: date
    """Das Geburtsdatum."""
    geschlecht: Geschlecht | None = None
    """Das optionale Geschlecht."""
    familienstand: Familienstand | None = None
    """Der optionale Familienstand."""
    homepage: HttpUrl | None = None
    """Die optionale URL der Homepage."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "nachname": "Test",
                "email": "test@acme.com",
                "kategorie": 1,
                "has_newsletter": True,
                "geburtsdatum": "2023-01-31",
                "geschlecht": "W",
                "familienstand": "L",
                "homepage": "https://test.rest",
            },
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Konvertierung der primitiven Attribute in ein Dictionary.

        :return: Dictionary mit den primitiven Patient-Attributen
        :rtype: dict[str, Any]
        """
        # Model von Pydantic in ein Dictionary konvertieren
        # https://docs.pydantic.dev/latest/concepts/serialization
        patient_dict = self.model_dump()
        patient_dict["id"] = None
        patient_dict["adresse"] = None
        patient_dict["rechnungen"] = []
        patient_dict["fachaerzte"] = []
        patient_dict["username"] = None
        patient_dict["erzeugt"] = None
        patient_dict["aktualisiert"] = None

        # HttpUrl ist ungeeignet fuer SQLAlchemy
        patient_dict["homepage"] = str(patient_dict["homepage"])
        return patient_dict

    def to_patient(self) -> Patient:
        """Konvertierung in ein Patient-Objekt für SQLAlchemy.

        :return: Patient-Objekt für SQLAlchemy
        :rtype: Patient
        """
        logger.debug("self={}", self)
        # Model von Pydantic in ein Dictionary konvertieren
        # https://docs.pydantic.dev/latest/concepts/serialization
        patient_dict = self.to_dict()

        # double star operator = double asterisk operator:
        # Dictionary auspacken als Schluessel-Wert-Paare
        # -> Namen der Schluessel = Namen der Funktionsargumente
        # https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters
        # https://docs.python.org/3/reference/expressions.html#dictionary-displays
        patient = Patient(**patient_dict)
        logger.debug("patient={}", patient)
        return patient
