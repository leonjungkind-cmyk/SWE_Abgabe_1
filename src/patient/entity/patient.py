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

"""Entity-Klasse für Patientendaten."""

from dataclasses import InitVar
from datetime import date, datetime
from typing import Any, Self

from loguru import logger
from sqlalchemy import JSON, Identity, func
from sqlalchemy.orm import Mapped, mapped_column, reconstructor, relationship

from patient.entity.adresse import Adresse
from patient.entity.base import Base
from patient.entity.facharzt import Facharzt
from patient.entity.familienstand import Familienstand
from patient.entity.geschlecht import Geschlecht
from patient.entity.rechnung import Rechnung

# https://docs.python.org/3/library/dataclasses.html
# vgl.: record in Java, data class in Kotlin
# eq=False: __eq__ wird *NICHT* generiert, alternativ: eigene Methode __eq__
# repr=False: __repr__ wird *NICHT* generiert, alternativ: eigene Methode __repr__
# frozen=True: immutable
# slots=True: statt Speicherung in __dict__ -> schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
# kw_only=True: Initialisierungs-Fkt darf nur mit "Keyword Arguments" aufgerufen werden
# @dataclass(frozen=True, slots=True, kw_only=True)


# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#native-support-for-dataclasses-mapped-as-orm-models
# https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
# "frozen" und "slots" wird in SQLAlchemy noch nicht unterstuetzt
# https://docs.sqlalchemy.org/en/20/core/type_basics.html#generic-camelcase-types
# noinspection PyUnresolvedReferences
class Patient(Base):
    """Entity-Klasse für Patientendaten."""

    __tablename__ = "patient"

    # es gibt auch die "Build-in" Funktion id(objekt)
    # https://docs.python.org/3/library/functions.html#id
    # https://stackoverflow.com/questions/15667189/what-is-the-id-function-used-for#answer-15667328
    nachname: Mapped[str]
    """Der Nachname."""

    kategorie: Mapped[int]
    """Die Kategorie."""

    has_newsletter: Mapped[bool]
    """Angabe, ob der Newsletter abonniert ist."""
    # https://docs.python.org/3/library/datetime.html
    geburtsdatum: Mapped[date]
    """Das Geburtsdatum."""

    # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#orm-declarative-mapped-column-enums
    geschlecht: Mapped[Geschlecht | None]
    """Das optionale Geschlecht."""

    familienstand: Mapped[Familienstand | None]
    """Der optionale Familienstand."""

    # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#json-types
    fachaerzte: InitVar[list[Facharzt] | None]
    """Die transiente Liste mit Fachärzten als Enum-Werte."""

    homepage: Mapped[str | None]
    """Die optionale URL der Homepage."""

    username: Mapped[str | None]
    """Der Benutzername für Login."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    email: Mapped[str] = mapped_column(unique=True)
    """Die eindeutige Emailadresse."""

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#relationship-configuration
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.innerjoin
    # https://docs.sqlalchemy.org/en/20/orm/cascades.html
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.cascade
    adresse: Mapped[Adresse] = relationship(
        back_populates="patient",
        innerjoin=True,
        cascade="save-update, delete",
    )
    """Die in einer 1:1-Beziehung referenzierte Adresse."""

    rechnungen: Mapped[list[Rechnung]] = relationship(
        back_populates="patient",
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Rechnungen."""

    # JSON ist in Python kein Typ, sondern nur Syntax fuer Strings mit codierten Daten
    # https://stackoverflow.com/questions/68154122/how-do-i-type-annotate-json-data-in-python#answer-68154189
    # https://github.com/python/typing/issues/182
    fachaerzte_json: Mapped[list[str] | None] = mapped_column(
        JSON,
        name="fachaerzte",
        init=False,
    )
    """Die persistente Liste der Fachärzte für ein JSON-Array."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Synchronisation."""

    # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#column-defaults
    erzeugt: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        default=None,
    )
    """Der Zeitstempel für das initiale INSERT in die DB-Tabelle."""

    aktualisiert: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
        default=None,
    )
    """Der Zeitstempel vom letzen UPDATE in der DB-Tabelle."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    __mapper_args__ = {"version_id_col": version}

    # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#using-non-mapped-dataclass-fields
    # https://docs.python.org/3/library/dataclasses.html#post-init-processing
    # Argumente in der Reihenfolge, wie die InitVar-Attribute deklariert sind
    def __post_init__(
        self,
        fachaerzte: list[Facharzt] | None,
    ) -> None:
        """Für SQLAlchemy: JSON-Array für DB-Spalte setzen für INSERT oder UPDATE.

        :param fachaerzte: Liste mit Fachärzten als Enum
        """
        logger.debug("fachaerzte={}", fachaerzte)
        logger.debug("self={}", self)
        # https://stackabuse.com/python-convert-list-to-string
        self.fachaerzte_json = (
            [facharzt_enum.name for facharzt_enum in fachaerzte]
            if fachaerzte is not None
            else None
        )
        logger.debug("self.fachaerzte_json={}", self.fachaerzte_json)

    # https://stackoverflow.com/questions/44270338/adding-to-sqlalchemy-mapping-class-non-db-attributes
    # https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.reconstructor
    # alternativ: @event.listens_for(User, 'load')
    # https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.InstanceEvents.load
    @reconstructor
    def on_load(self) -> None:
        """Auslesen aus der DB: die Enum-Liste durch die DB-Strings initialisieren."""
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        self.fachaerzte = (  # pyright: ignore[reportAttributeAccessIssue]
            [Facharzt[facharzt_name] for facharzt_name in self.fachaerzte_json]
            if self.fachaerzte_json is not None
            else []
        )
        logger.debug(
            "fachaerzte={}",
            self.fachaerzte,  # pyright: ignore[reportAttributeAccessIssue]
        )

    def set(self, patient: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param patient: Patient-Objekt mit den aktuellen Daten
        """
        self.nachname = patient.nachname
        self.email = patient.email
        self.kategorie = patient.kategorie
        self.has_newsletter = patient.has_newsletter
        self.geburtsdatum = patient.geburtsdatum

    def __eq__(self, other: Any) -> bool:
        """Vergleich auf Gleicheit, ohne Joins zu verursachen."""
        # Vergleich der Referenzen: id(self) == id(other)
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    def __repr__(self) -> str:
        """Ausgabe eines Patienten als String, ohne Joins zu verursachen."""
        return (
            f"Patient(id={self.id}, version={self.version}, "
            + f"nachname={self.nachname}, email={self.email}, "
            + f"kategorie={self.kategorie}, has_newsletter={self.has_newsletter}, "
            + f"geburtsdatum={self.geburtsdatum}, homepage={self.homepage}, "
            + f"geschlecht={self.geschlecht}, familienstand={self.familienstand}, "
            + f"fachaerzte_json={self.fachaerzte_json}, username={self.username}, "
            + f"erzeugt={self.erzeugt}, aktualisiert={self.aktualisiert})"
        )
