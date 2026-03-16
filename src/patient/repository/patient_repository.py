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

"""Repository fuer persistente Patientendaten."""

# "list" ist eine mutable "Sequence"
# https://docs.python.org/3/library/stdtypes.html#lists
# https://docs.python.org/3/library/stdtypes.html#typesseq
from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from patient.entity import Patient
from patient.repository.pageable import Pageable
from patient.repository.slice import Slice

__all__ = ["PatientRepository"]


class PatientRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Patient."""

    def find_by_id(self, patient_id: int | None, session: Session) -> Patient | None:
        """Suche mit der Patient-ID.

        :param patient_id: ID des gesuchten Patienten
        :param session: Session für SQLAlchemy
        :return: Der gefundene Patient oder None
        :rtype: Patient | None
        """
        logger.debug("patient_id={}", patient_id)  # NOSONAR

        if patient_id is None:
            return None

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#relationship-loading-with-loader-options
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#sqlalchemy.orm.joinedload
        statement: Final = (
            select(Patient)
            .options(joinedload(Patient.adresse))
            .where(Patient.id == patient_id)
        )
        patient: Final = session.scalar(statement)

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#get-by-primary-key
        # patient: Final[Patient | None] = session.get(Patient, patient_id)

        logger.debug("{}", patient)
        return patient

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
        session: Session,
    ) -> Slice[Patient]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter als Dictionary
        :param pageable: Anzahl Datensätze und Seitennummer
        :param session: Session für SQLAlchemy
        :return: Tupel, d.h. readonly Liste, der gefundenen Patienten oder leeres Tupel
        :rtype: Slice[Patient]
        """
        log_str: Final = "{}"
        logger.debug(log_str, suchparameter)
        if not suchparameter:
            return self._find_all(pageable=pageable, session=session)

        # Iteration ueber die Schluessel des Dictionaries mit den Suchparameter
        for key, value in suchparameter.items():
            if key == "email":
                patient = self._find_by_email(email=value, session=session)
                logger.debug(log_str, patient)
                return (
                    Slice(content=(patient,), total_elements=1)
                    if patient is not None
                    else Slice(content=(), total_elements=0)
                )
            if key == "nachname":
                patienten = self._find_by_nachname(
                    teil=value, pageable=pageable, session=session
                )
                logger.debug(log_str, patienten)
                return patienten
        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Patient]:
        logger.debug("aufgerufen")
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Patient)
                .options(joinedload(Patient.adresse))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (select(Patient).options(joinedload(Patient.adresse)))
        )
        patienten: Final = (session.scalars(statement)).all()
        anzahl: Final = self._count_all_rows(session)
        patient_slice: Final = Slice(content=tuple(patienten), total_elements=anzahl)
        logger.debug("patient_slice={}", patient_slice)
        return patient_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Patient)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def _find_by_email(self, email: str, session: Session) -> Patient | None:
        """Einen Patienten anhand der Emailadresse suchen.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: Gefundener Patient, falls es einen Patienten gibt, sonst None
        :rtype: Patient | None
        """
        logger.debug("email={}", email)  # NOSONAR
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            select(Patient)
            .options(joinedload(Patient.adresse))
            .where(Patient.email == email)
        )
        patient: Final = session.scalar(statement)
        logger.debug("{}", patient)
        return patient

    def _find_by_nachname(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Patient]:
        logger.debug("teil={}", teil)
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Patient)
                .options(joinedload(Patient.adresse))
                .filter(Patient.nachname.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Patient)
                .options(joinedload(Patient.adresse))
                .filter(Patient.nachname.ilike(f"%{teil}%"))
            )
        )
        patienten: Final = session.scalars(statement).all()
        anzahl: Final = self._count_rows_nachname(teil, session)
        patient_slice: Final = Slice(content=tuple(patienten), total_elements=anzahl)
        logger.debug("{}", patient_slice)
        return patient_slice

    def _count_rows_nachname(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count())
            .select_from(Patient)
            .filter(Patient.nachname.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def exists_email(self, email: str, session: Session) -> bool:
        """Abfrage, ob es die Emailadresse bereits gibt.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(func.count()).where(Patient.email == email)
        anzahl: Final = session.scalar(statement)
        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def exists_email_other_id(
        self,
        email: str,
        patient_id: int,
        session: Session,
    ) -> bool:
        """Abfrage, ob es die Emailadresse bei einer anderen Patient-ID bereits gibt.

        :param email: Emailadresse
        :param patient_id: eigene Patient-ID
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(Patient.id).where(Patient.email == email)
        id_db: Final = session.scalar(statement)
        logger.debug("id_db={}", id_db)
        return id_db is not None and id_db != patient_id

    def create(self, patient: Patient, session: Session) -> Patient:
        """Speichere einen neuen Patienten ab.

        :param patient: Die Daten des neuen Patienten ohne ID
        :param session: Session für SQLAlchemy
        :return: Der neu angelegte Patient mit generierter ID
        :rtype: Patient
        """
        logger.debug(
            "patient={}, patient.adresse={}, patient.rechnungen={}",
            patient,
            patient.adresse,
            patient.rechnungen,
        )
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#adding-new-or-existing-items
        session.add(instance=patient)
        # flush(), damit die ID aus der Sequence vor COMMIT fuer Logging verfuegbar ist
        # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#flushing
        session.flush(objects=[patient])
        logger.debug("patient_id={}", patient.id)
        return patient

    def update(self, patient: Patient, session: Session) -> Patient | None:
        """Aktualisiere einen Patienten.

        :param patient: Die neuen Patientendaten
        :param session: Session für SQLAlchemy
        :return: Der aktualisierte Patient oder None, falls kein Patienten mit der ID
        existiert
        :rtype: Patient | None
        """
        logger.debug("{}", patient)

        if (
            patient_db := self.find_by_id(patient_id=patient.id, session=session)
        ) is None:
            # Patientendaten wurden i.a. zuvor in der Session aktualisiert
            return None

        # session.add(patient_db) nicht notwendig, da bereits in der Session zugegriffen
        # CAVEAT: Die erhoehte Versionsnummer ist erst *nach* COMMIT sichtbar

        logger.debug("{}", patient_db)
        return patient_db

    def delete_by_id(self, patient_id: int, session: Session) -> None:
        """Lösche die Daten zu einem Patienten.

        :param patient_id: Die ID des zu löschenden Patienten
        :param session: Session für SQLAlchemy
        """
        logger.debug("patient_id={}", patient_id)

        # delete(Patient).where(Patient.patient_id == patient_id) OHNE cascade
        # "walrus operator" https://peps.python.org/pep-0572
        if (patient := self.find_by_id(patient_id=patient_id, session=session)) is None:
            return
        session.delete(patient)
        logger.debug("ok")

    def find_nachnamen(self, teil: str, session: Session) -> Sequence[str]:
        """Suche Nachnamen zu einem Teilstring.

        :param teil: Teilstring zu den gesuchten Nachnamen
        :param session: Session für SQLAlchemy
        :return: Liste der gefundenen Nachnamen oder eine leere Liste
        :rtype: Sequence[str]
        """
        logger.debug("teil={}", teil)

        statement: Final = (
            select(Patient.nachname)
            .filter(Patient.nachname.ilike(f"%{teil}%"))
            .distinct()
        )
        nachnamen: Final = (session.scalars(statement)).all()

        logger.debug("nachnamen={}", nachnamen)
        return nachnamen

    def exists_username(self, username: str | None, session: Session) -> bool:
        """Abfrage, ob es den Benutzernamen bereits gibt.

        :param username: Benutzername
        :param session: Session für SQLAlchemy
        :return: True, falls es den Benutzernamen bereits gibt
        :rtype: bool
        """
        logger.debug("username={}", username)
        if username is None:
            return False

        statement: Final = select(Patient.username).filter_by(username=username)
        username_db: Final = session.scalar(statement)
        logger.debug("username_db={}", username_db)
        return username_db is not None
