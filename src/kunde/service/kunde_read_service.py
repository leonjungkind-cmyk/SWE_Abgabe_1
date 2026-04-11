"""Geschäftslogik zum Lesen von Kundendaten."""

from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger

from kunde.repository import KundeRepository, Session
from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice
from kunde.security import Role, User
from kunde.service.exceptions import ForbiddenError, NotFoundError
from kunde.service.kunde_dto import KundeDTO

__all__ = ["KundeReadService"]


class KundeReadService:
    """Lese-Operationen mit fachlicher Logik für die Kundenverwaltung."""

    def __init__(self, repo: KundeRepository) -> None:
        """Initialisierung mit dem benötigten KundeRepository."""
        self.repo: KundeRepository = repo

    def find_by_id(self, kunde_id: int, user: User) -> KundeDTO:
        """Lädt einen einzelnen Kunden über seine ID.

        :param kunde_id: Primärschlüssel des gesuchten Kunden
        :param user: aktueller User aus dem Token
        :return: Gefundener Kunde als DTO
        :rtype: KundeDTO
        :raises NotFoundError: Wenn kein Kunde existiert
        :raises ForbiddenError: Wenn Zugriff nicht erlaubt
        """
        logger.debug("kunde_id={}, user={}", kunde_id, user)

        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            kunde = self.repo.find_by_id(
                kunde_id=kunde_id,
                session=session,
            )

            if kunde is None:
                if user_is_admin:
                    message: Final = f"Kein Kunde mit der ID {kunde_id}"
                    logger.debug("NotFoundError: {}", message)
                    raise NotFoundError(kunde_id=kunde_id)

                raise ForbiddenError

            if kunde.username != user.username and not user_is_admin:
                logger.debug(
                    "kunde.username={}, user.username={}, user.roles={}",
                    kunde.username,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            kunde_dto: Final = KundeDTO(kunde)
            session.commit()

        logger.debug("{}", kunde_dto)
        return kunde_dto

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
    ) -> Slice[KundeDTO]:
        """Sucht Kunden anhand der übergebenen Filter und gibt eine Seite zurück.

        :param suchparameter: Filterkriterien als Schlüssel-Wert-Paare
        :param pageable: Gewünschte Seite und Einträge pro Seite
        :return: Slice mit DTO-Treffern der aktuellen Seite
        :rtype: Slice[KundeDTO]
        :raises NotFoundError: Wenn keine Kunden den Kriterien entsprechen
        """
        logger.debug("{}", suchparameter)

        with Session() as session:
            kunde_slice: Final = self.repo.find(
                suchparameter=suchparameter,
                pageable=pageable,
                session=session,
            )

            if len(kunde_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            kunden_dto: Final = tuple(
                KundeDTO(kunde) for kunde in kunde_slice.content
            )
            session.commit()

        kunden_dto_slice = Slice(
            content=kunden_dto,
            total_elements=kunde_slice.total_elements,
        )
        logger.debug("{}", kunden_dto_slice)
        return kunden_dto_slice

    def find_nachnamen(self, teil: str) -> Sequence[str]:
        """Gibt alle Nachnamen zurück, die den übergebenen Teilstring enthalten.

        :param teil: Teilstring, nach dem in Nachnamen gesucht wird
        :return: Deduplizierte Sequenz passender Nachnamen
        :rtype: Sequence[str]
        :raises NotFoundError: Wenn keine passenden Nachnamen gefunden wurden
        """
        logger.debug("teil={}", teil)

        with Session() as session:
            nachnamen: Final = self.repo.find_nachnamen(
                teil=teil,
                session=session,
            )
            session.commit()

        logger.debug("{}", nachnamen)
        if len(nachnamen) == 0:
            raise NotFoundError

        return nachnamen
