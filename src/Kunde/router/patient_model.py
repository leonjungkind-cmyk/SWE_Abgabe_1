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

"""Pydantic-Model für die Patientendaten."""

from typing import Annotated, Final

from loguru import logger
from pydantic import StringConstraints

from patient.entity import Facharzt, Patient
from patient.router.adresse_model import AdresseModel
from patient.router.patient_update_model import PatientUpdateModel
from patient.router.rechnung_model import RechnungModel

__all__ = ["PatientModel"]


# https://towardsdatascience.com/pydantic-or-dataclasses-why-not-both-convert-between-them-ba382f0f9a9c
class PatientModel(PatientUpdateModel):
    """Pydantic-Model für die Patientendaten."""

    adresse: AdresseModel
    """Die zugehörige Adresse."""
    rechnungen: list[RechnungModel]
    """Die Liste der Rechnungen."""
    fachaerzte: list[Facharzt]
    """Die Liste mit Fachärzten als Enum-Werte."""
    # https://docs.pydantic.dev/usage/types
    username: Annotated[str, StringConstraints(max_length=20)]
    """Der Benutzername für Login."""

    def to_patient(self) -> Patient:
        """Konvertierung in ein Patient-Objekt für SQLAlchemy.

        :return: Patient-Objekt für SQLAlchemy
        :rtype: Patient
        """
        logger.debug("self={}", self)
        patient_dict = self.to_dict()
        patient_dict["fachaerzte"] = self.fachaerzte
        # bei Updates wird "username" nicht aktualisiert bzw. muss gleich bleiben
        # in PatientUpdateModel wird "username" deshalb auf None gesetzt
        patient_dict["username"] = self.username

        patient: Final = Patient(**patient_dict)
        patient.adresse = self.adresse.to_adresse()
        patient.rechnungen = [
            rechnung_model.to_rechnung() for rechnung_model in self.rechnungen
        ]
        logger.debug("patient={}", patient)
        return patient
