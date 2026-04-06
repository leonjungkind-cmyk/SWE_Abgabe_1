"""Repository für persistente Kundendaten."""

from collections.abc import Mapping
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from kunde.entity import Kunde
from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice

__all__ = ["KundeRepository"]


class KundeRepository:
    """Datenbankzugriffe für die Entity-Klasse Kunde."""

    def find_by_id(self, kunde_id: int | None, session: Session) -> Kunde | None:
        """Lädt einen Kunden anhand seiner ID.

        :param kunde_id: Primärschlüssel des gesuchten Kunden
        :param session: Aktive SQLAlchemy-Session
        :return: Gefundener Kunde oder None, falls kein Treffer
        :rtype: Kunde | None
        """
        logger.debug("kunde_id={}", kunde_id)

        if kunde_id is None:
            return None

        statement: Final = (
            select(Kunde)
            .options(
                joinedload(Kunde.adresse),
                joinedload(Kunde.bestellungen),
            )
            .where(Kunde.id == kunde_id)
        )
        kunde: Final = session.scalar(statement)

        logger.debug("{}", kunde)
        return kunde

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
        session: Session,
    ) -> Slice[Kunde]:
        """Filtert Kunden nach den übergebenen Suchkriterien.

        :param suchparameter: Filterkriterien als Schlüssel-Wert-Paare
        :param pageable: Seitennummer und Einträge pro Seite
        :param session: Aktive SQLAlchemy-Session
        :return: Slice mit Treffern der aktuellen Seite und Gesamtanzahl
        :rtype: Slice[Kunde]
        """
        log_str: Final = "{}"
        logger.debug(log_str, suchparameter)

        if not suchparameter:
            return self._find_all(pageable=pageable, session=session)

        for key, value in suchparameter.items():
            if key == "email":
                kunde = self._find_by_email(email=value, session=session)
                logger.debug(log_str, kunde)
                return (
                    Slice(content=(kunde,), total_elements=1)
                    if kunde is not None
                    else Slice(content=(), total_elements=0)
                )
            if key == "nachname":
                kunden = self._find_by_nachname(
                    teil=value, pageable=pageable, session=session
                )
                logger.debug(log_str, kunden)
                return kunden

        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Kunde]:
        logger.debug("aufgerufen")
        offset = pageable.number * pageable.size

        statement: Final = (
            (
                select(Kunde)
                .options(
                    joinedload(Kunde.adresse),
                    joinedload(Kunde.bestellungen),
                )
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Kunde)
                .options(
                    joinedload(Kunde.adresse),
                    joinedload(Kunde.bestellungen),
                )
            )
        )

        kunden: Final = session.scalars(statement).unique().all()
        anzahl: Final = self._count_all_rows(session)
        kunde_slice: Final = Slice(content=tuple(kunden), total_elements=anzahl)
        logger.debug("kunde_slice={}", kunde_slice)
        return kunde_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Kunde)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def _find_by_email(self, email: str, session: Session) -> Kunde | None:
        """Sucht einen Kunden anhand seiner genauen Emailadresse.

        :param email: Vollständige Emailadresse
        :param session: Aktive SQLAlchemy-Session
        :return: Passender Kunde oder None
        :rtype: Kunde | None
        """
        logger.debug("email={}", email)

        statement: Final = (
            select(Kunde)
            .options(
                joinedload(Kunde.adresse),
                joinedload(Kunde.bestellungen),
            )
            .where(Kunde.email == email)
        )
        kunde: Final = session.scalar(statement)
        logger.debug("{}", kunde)
        return kunde

    def _find_by_nachname(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Kunde]:
        logger.debug("teil={}", teil)
        offset = pageable.number * pageable.size

        statement: Final = (
            (
                select(Kunde)
                .options(
                    joinedload(Kunde.adresse),
                    joinedload(Kunde.bestellungen),
                )
                .filter(Kunde.nachname.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Kunde)
                .options(
                    joinedload(Kunde.adresse),
                    joinedload(Kunde.bestellungen),
                )
                .filter(Kunde.nachname.ilike(f"%{teil}%"))
            )
        )

        kunden: Final = session.scalars(statement).unique().all()
        anzahl: Final = self._count_rows_nachname(teil, session)
        kunde_slice: Final = Slice(content=tuple(kunden), total_elements=anzahl)
        logger.debug("{}", kunde_slice)
        return kunde_slice

    def _count_rows_nachname(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count())
            .select_from(Kunde)
            .filter(Kunde.nachname.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def find_nachnamen(self, teil: str, session: Session) -> list[str]:
        """Liefert alle eindeutigen Nachnamen, die den Teilstring enthalten.

        :param teil: Gesuchter Teilstring im Nachnamen
        :param session: Aktive SQLAlchemy-Session
        :return: Deduplizierte Liste passender Nachnamen
        :rtype: list[str]
        """
        logger.debug("teil={}", teil)

        statement: Final = (
            select(Kunde.nachname)
            .where(Kunde.nachname.ilike(f"%{teil}%"))
            .distinct()
        )
        nachnamen: Final = list(session.scalars(statement))

        logger.debug("nachnamen={}", nachnamen)
        return nachnamen

    def exists_email(self, email: str, session: Session) -> bool:
        """Prüft, ob eine Emailadresse bereits einem Kunden zugeordnet ist.

        :param email: Zu prüfende Emailadresse
        :param session: Aktive SQLAlchemy-Session
        :return: True, wenn die Adresse bereits vergeben ist
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(func.count()).where(Kunde.email == email)
        anzahl: Final = session.scalar(statement)

        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def create(self, kunde: Kunde, session: Session) -> Kunde:
        """Legt einen neuen Kunden in der Datenbank an.

        :param kunde: Zu speichernde Kundendaten (noch ohne ID)
        :param session: Aktive SQLAlchemy-Session
        :return: Gespeicherter Kunde mit vergebener ID
        :rtype: Kunde
        """
        logger.debug(
            "kunde={}, kunde.adresse={}, kunde.bestellungen={}",
            kunde,
            kunde.adresse,
            kunde.bestellungen,
        )

        session.add(instance=kunde)
        session.flush(objects=[kunde])

        logger.debug("kunde_id={}", kunde.id)
        return kunde

    def exists_email_other_id(
        self,
        kunde_id: int,
        email: str,
        session: Session,
    ) -> bool:
        """Prüft, ob eine Emailadresse bereits bei einem anderen Kunden existiert.

        :param kunde_id: ID des aktuellen Kunden
        :param email: Zu prüfende Emailadresse
        :param session: Aktive SQLAlchemy-Session
        :return: True, wenn die Adresse bei einem anderen Kunden existiert
        :rtype: bool
        """
        logger.debug("kunde_id={}, email={}", kunde_id, email)

        statement: Final = (
            select(func.count())
            .select_from(Kunde)
            .where(Kunde.email == email)
            .where(Kunde.id != kunde_id)
        )
        anzahl: Final = session.scalar(statement)

        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def update(self, kunde: Kunde, session: Session) -> Kunde | None:
        """Aktualisiert einen bestehenden Kunden.

        :param kunde: Bereits geladener und veränderter Kunde
        :param session: Aktive SQLAlchemy-Session
        :return: Aktualisierter Kunde oder None
        :rtype: Kunde | None
        """
        logger.debug("kunde={}", kunde)
        session.add(kunde)
        session.flush()
        return kunde

    def delete_by_id(self, kunde_id: int, session: Session) -> None:
        """Löscht einen Kunden anhand seiner ID.

        :param kunde_id: ID des zu löschenden Kunden
        :param session: Aktive SQLAlchemy-Session
        """
        logger.debug("kunde_id={}", kunde_id)

        kunde: Final = self.find_by_id(kunde_id=kunde_id, session=session)
        if kunde is None:
            return

        session.delete(kunde)
        session.flush()
