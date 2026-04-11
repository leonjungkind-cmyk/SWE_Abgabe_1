"""Geschäftslogik zum Schreiben von Kundendaten."""

from typing import Final

from loguru import logger

from kunde.entity import Kunde
from kunde.repository import KundeRepository, Session
from kunde.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    VersionOutdatedError,
)
from kunde.service.kunde_dto import KundeDTO

__all__ = ["KundeWriteService"]


class KundeWriteService:
    """Service-Klasse mit Geschäftslogik für Kunde."""

    def __init__(self, repo: KundeRepository) -> None:
        """Konstruktor mit abhängigem KundeRepository.

        :param repo: Repository für Kundendaten
        """
        self.repo: KundeRepository = repo

    def create(self, kunde: Kunde) -> KundeDTO:
        """Einen neuen Kunden anlegen.

        :param kunde: Der neue Kunde ohne ID
        :return: Der neu angelegte Kunde mit generierter ID
        :rtype: KundeDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "kunde={}, adresse={}, bestellungen={}",
            kunde,
            kunde.adresse,
            kunde.bestellungen,
        )

        email: Final = kunde.email

        with Session() as session:
            if self.repo.exists_email(email=email, session=session):
                raise EmailExistsError(email=email)

            kunde_db: Final = self.repo.create(
                kunde=kunde,
                session=session,
            )
            kunde_dto: Final = KundeDTO(kunde_db)

            session.commit()

        logger.debug("kunde_dto={}", kunde_dto)
        return kunde_dto

    def update(self, kunde: Kunde, kunde_id: int, version: int) -> KundeDTO:
        """Daten eines Kunden ändern.

        :param kunde: Die neuen Daten
        :param kunde_id: ID des zu aktualisierenden Kunden
        :param version: Version für optimistische Synchronisation
        :return: Der aktualisierte Kunde
        :rtype: KundeDTO
        :raises NotFoundError: Falls der zu aktualisierende Kunde nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug("kunde_id={}, version={}, {}", kunde_id, version, kunde)

        with Session() as session:
            if (
                kunde_db := self.repo.find_by_id(
                    kunde_id=kunde_id,
                    session=session,
                )
            ) is None:
                raise NotFoundError(kunde_id)

            if kunde_db.version > version:
                raise VersionOutdatedError(version)

            email: Final = kunde.email
            if email != kunde_db.email and self.repo.exists_email_other_id(
                kunde_id=kunde_id,
                email=email,
                session=session,
            ):
                raise EmailExistsError(email)

            kunde_db.set(kunde)

            if (
                kunde_updated := self.repo.update(
                    kunde=kunde_db,
                    session=session,
                )
            ) is None:
                raise NotFoundError(kunde_id)

            kunde_dto: Final = KundeDTO(kunde_updated)
            logger.debug("kunde_dto={}", kunde_dto)

            session.commit()

            # Version erst nach Commit sichtbar
            kunde_dto.version += 1

            return kunde_dto

    def delete_by_id(self, kunde_id: int) -> None:
        """Einen Kunden anhand seiner ID löschen.

        :param kunde_id: ID des zu löschenden Kunden
        """
        logger.debug("kunde_id={}", kunde_id)

        with Session() as session:
            self.repo.delete_by_id(
                kunde_id=kunde_id,
                session=session,
            )
            session.commit()
