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

"""Geschäftslogik zum Lesen von Patientendaten."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Final

from loguru import logger
from openpyxl import Workbook  # pyright: ignore[reportMissingModuleSource]

from patient.config import excel_enabled
from patient.repository import (
    Pageable,
    PatientRepository,
    Session,
    Slice,
)
from patient.security import Role, User
from patient.service.exceptions import ForbiddenError, NotFoundError
from patient.service.patient_dto import PatientDTO

__all__ = ["PatientService"]


class PatientService:
    """Service-Klasse mit Geschäftslogik für Patient."""

    def __init__(self, repo: PatientRepository) -> None:
        """Konstruktor mit abhängigem PatientRepository."""
        self.repo: PatientRepository = repo

    def find_by_id(self, patient_id: int, user: User) -> PatientDTO:
        """Suche mit der Patient-ID.

        :param patient_id: ID für die Suche
        :param user: User aus dem Token
        :return: Der gefundene Patient
        :rtype: PatientDTO
        :raises NotFoundError: Falls kein Patient gefunden
        :raises ForbiddenError: Falls die Patientendaten nicht gelesen werden dürfen
        """
        logger.debug("patient_id={}, user={}", patient_id, user)

        # Session-Objekt ist die Schnittstelle zur DB, nutzt intern ein Transaktionsobj.
        # implizites "autobegin()" bei einem with-Block
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#opening-and-closing-a-session
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#auto-begin
        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            if (
                patient := self.repo.find_by_id(patient_id=patient_id, session=session)
            ) is None:
                if user_is_admin:
                    message: Final = f"Kein Patient mit der ID {patient_id}"
                    logger.debug("NotFoundError: {}", message)
                    # "Throw Exceptions Instead of Returning Errors"
                    raise NotFoundError(patient_id=patient_id)
                logger.debug("nicht admin")
                raise ForbiddenError

            if patient.username != user.username and not user_is_admin:
                logger.debug(
                    "patient.username={}, user.username={}, user.roles={}",
                    patient.username,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            patient_dto: Final = PatientDTO(patient)
            session.commit()

        logger.debug("{}", patient_dto)
        return patient_dto

    # ab Python 3.9 (2019) ist der Element-Type in eckigen Klammern und
    # der Name von eingebauten Collections ist kleingeschrieben.
    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
    ) -> Slice[PatientDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter
        :return: Liste der gefundenen Patienten
        :rtype: Slice[PatientDTO]
        :raises NotFoundError: Falls keine Patienten gefunden wurden
        """
        logger.debug("{}", suchparameter)
        with Session() as session:
            patient_slice: Final = self.repo.find(
                suchparameter=suchparameter, pageable=pageable, session=session
            )
            if len(patient_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            # tuple mit einem "Generator"-Ausdruck
            # vgl. List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
            patienten_dto: Final = tuple(
                PatientDTO(patient) for patient in patient_slice.content
            )
            session.commit()

        if excel_enabled:
            self._create_excelsheet(patienten_dto)
        patienten_dto_slice = Slice(
            content=patienten_dto, total_elements=patient_slice.total_elements
        )
        logger.debug("{}", patienten_dto_slice)
        return patienten_dto_slice

    def find_nachnamen(self, teil: str) -> Sequence[str]:
        """Suche Nachnamen zu einem Teilstring.

        :param teil: Teilstring der gesuchten Nachnamen
        :return: Liste der gefundenen Nachnamen oder eine leere Liste
        :rtype: list[str]
        :raises NotFoundError: Falls keine Nachnamen gefunden wurden
        """
        logger.debug("teil={}", teil)
        with Session() as session:
            nachnamen: Final = self.repo.find_nachnamen(teil=teil, session=session)
            session.commit()

        logger.debug("{}", nachnamen)
        if len(nachnamen) == 0:
            raise NotFoundError
        return nachnamen

    def _create_excelsheet(self, patienten: tuple[PatientDTO, ...]) -> None:
        """Ein Excelsheet mit den gefundenen Patienten erstellen.

        :param patienten: Patientendaten für das Excelsheet
        """
        # https://automatetheboringstuff.com/2e/chapter13
        workbook: Final = Workbook()
        worksheet: Final = workbook.active
        if worksheet is None:
            return

        worksheet.append(["Nachname", "Emailadresse", "Geschlecht", "Familienstand"])
        for patient in patienten:
            geschlecht = (
                str(patient.geschlecht) if patient.geschlecht is not None else "N/A"
            )
            familienstand = (
                str(patient.familienstand)
                if patient.familienstand is not None
                else "N/A"
            )
            worksheet.append((
                patient.nachname,
                patient.email,
                geschlecht,
                familienstand,
            ))

        timestamp: Final = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        workbook.save(f"patienten-{timestamp}.xlsx")
