# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Geschäftslogik zum Schreiben von Patientendaten."""

from typing import Final

from loguru import logger

from patient.entity import Patient
from patient.repository import PatientRepository, Session
from patient.security import User, UserService
from patient.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from patient.service.mailer import send_mail
from patient.service.patient_dto import PatientDTO

__all__ = ["PatientWriteService"]


class PatientWriteService:
    """Service-Klasse mit Geschäftslogik für Patient."""

    def __init__(self, repo: PatientRepository, user_service: UserService) -> None:
        """Konstruktor mit abhängigem PatientRepository und UserService."""
        self.repo: PatientRepository = repo
        self.user_service: UserService = user_service

    def create(self, patient: Patient) -> PatientDTO:
        """Einen neuen Patienten anlegen.

        :param patient: Der neue Patient ohne ID
        :return: Der neu angelegte Patient mit generierter ID
        :rtype: PatientDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "patient={}, adresse={}, rechnungen={}",
            patient,
            patient.adresse,
            patient.rechnungen,
        )

        username: Final = patient.username
        if username is None:
            raise ValueError

        # https://www.keycloak.org/docs-api/latest/rest-api:
        # GET /admin/realms/{realm}/users
        if self.user_service.username_exists(username):
            raise UsernameExistsError(username)

        email: Final = patient.email
        if self.user_service.email_exists(email):
            raise EmailExistsError(email=email)

        user: Final = User(
            username=username,
            email=patient.email,
            nachname=patient.nachname,
            vorname=patient.nachname,
            password="p",  # noqa: S106 # NOSONAR
            roles=[],
        )
        user_id = self.user_service.create_user(user)
        logger.debug("user_id={}", user_id)

        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            if self.repo.exists_email(email=email, session=session):
                raise EmailExistsError(email=email)

            patient_db: Final = self.repo.create(patient=patient, session=session)
            patient_dto: Final = PatientDTO(patient_db)
            session.commit()

        # TODO User aus Keycloak loeschen, falls die DB-Transaktion fehlschlaegt

        send_mail(patient_dto=patient_dto)
        logger.debug("patient_dto={}", patient_dto)
        return patient_dto

    def update(self, patient: Patient, patient_id: int, version: int) -> PatientDTO:
        """Daten eines Patienten ändern.

        :param patient: Die neuen Daten
        :param patient_id: ID des zu aktualisierenden Patienten
        :param version: Version für optimistische Synchronisation
        :return: Der aktualisierte Patient
        :rtype: PatientDTO
        :raises NotFoundError: Falls der zu aktualisierende Patient nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug("patient_id={}, version={}, {}", patient_id, version, patient)

        with Session() as session:
            if (
                patient_db := self.repo.find_by_id(
                    patient_id=patient_id, session=session
                )
            ) is None:
                raise NotFoundError(patient_id)
            if patient_db.version > version:
                raise VersionOutdatedError(version)

            email: Final = patient.email
            if email != patient_db.email and self.repo.exists_email_other_id(
                patient_id=patient_id,
                email=email,
                session=session,
            ):
                raise EmailExistsError(email)

            patient_db.set(patient)
            if (
                patient_updated := self.repo.update(patient=patient_db, session=session)
            ) is None:
                raise NotFoundError(patient_id)
            patient_dto: Final = PatientDTO(patient_updated)
            logger.debug("{}", patient_dto)

            session.commit()
            # CAVEAT: Die erhoehte Versionsnummer ist erst COMMIT sichtbar
            patient_dto.version += 1
            return patient_dto

    def delete_by_id(self, patient_id: int) -> None:
        """Einen Patienten anhand seiner ID löschen.

        :param patient_id: ID des zu löschenden Patienten
        """
        logger.debug("patient_id={}", patient_id)
        with Session() as session:
            self.repo.delete_by_id(patient_id=patient_id, session=session)
            session.commit()
