"""Geschaeftslogik zum Lesen von Kundendaten."""

from typing import Final

from kunde.repository import KundeRepository, Session
from kunde.service.kunde_dto import KundeDTO

__all__ = ["KundeReadService"]


class KundeReadService:
    """Service-Klasse mit Geschaeftslogik fuer Lesezugriffe auf Kunde."""

    def __init__(self, repo: KundeRepository) -> None:
        """Konstruktor mit abhaengigem KundeRepository.

        :param repo: Repository fuer Kundendaten
        """
        self.repo: KundeRepository = repo

    def find_by_id(self, kunde_id: int) -> KundeDTO | None:
        """Suche einen Kunden ueber seine ID.

        :param kunde_id: ID des gesuchten Kunden
        :return: KundeDTO bei Treffer, sonst None
        :rtype: KundeDTO | None
        """
        with Session() as session:
            kunde_db: Final = self.repo.find_by_id(kunde_id=kunde_id, session=session)

        if kunde_db is None:
            return None

        kunde_dto: Final = KundeDTO(kunde_db)
        return kunde_dto
