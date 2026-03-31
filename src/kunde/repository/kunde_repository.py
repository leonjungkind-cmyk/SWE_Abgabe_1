# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Repository für persistente Kundendaten."""

from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from kunde.entity import Kunde

__all__ = ["KundeRepository"]


class KundeRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Kunde."""

    def find_by_id(self, kunde_id: int | None, session: Session) -> Kunde | None:
        """Suche mit der Kunden-ID.

        :param kunde_id: ID des gesuchten Kunden
        :param session: Session für SQLAlchemy
        :return: Der gefundene Kunde oder None
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

    def exists_email(self, email: str, session: Session) -> bool:
        """Abfrage, ob es die Emailadresse bereits gibt.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, sonst False
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(func.count()).where(Kunde.email == email)
        anzahl: Final = session.scalar(statement)

        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def create(self, kunde: Kunde, session: Session) -> Kunde:
        """Speichere einen neuen Kunden ab.

        :param kunde: Die Daten des neuen Kunden ohne ID
        :param session: Session für SQLAlchemy
        :return: Der neu angelegte Kunde mit generierter ID
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
