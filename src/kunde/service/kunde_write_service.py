"""Geschäftslogik zum Schreiben von Kundendaten."""

from typing import Final

from loguru import logger

from kunde.entity import Kunde
from kunde.repository import KundeRepository, Session
from kunde.service.exceptions import EmailExistsError
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

            kunde_db: Final = self.repo.create(kunde=kunde, session=session)
            kunde_dto: Final = KundeDTO(kunde_db)
            session.commit()

        logger.debug("kunde_dto={}", kunde_dto)
        return kunde_dto
