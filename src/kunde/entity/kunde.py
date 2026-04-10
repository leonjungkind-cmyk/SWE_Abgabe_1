"""Entity-Klasse für Kundendaten."""

from typing import Any, Self

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.bestellung import Bestellung


class Kunde(Base):
    """Entity-Klasse für Kundendaten."""

    __tablename__ = "kunde"

    nachname: Mapped[str]
    """Der Nachname."""

    username: Mapped[str | None]
    """Der Benutzername für Login und Zugriffsschutz."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID."""

    email: Mapped[str] = mapped_column(unique=True)
    """Die eindeutige Emailadresse."""

    adresse: Mapped[Adresse] = relationship(
        back_populates="kunde",
        innerjoin=True,
        cascade="save-update, delete",
    )
    """Die in einer 1:1-Beziehung referenzierte Adresse."""

    bestellungen: Mapped[list[Bestellung]] = relationship(
        back_populates="kunde",
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Bestellungen."""

    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Nebenläufigkeitskontrolle."""

    __mapper_args__ = {"version_id_col": version}

    def set(self, kunde: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update."""
        self.nachname = kunde.nachname
        self.email = kunde.email
        self.username = kunde.username

    def __eq__(self, other: Any) -> bool:
        """Vergleich auf Gleichheit, ohne Joins zu verursachen."""
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    def __repr__(self) -> str:
        """Ausgabe eines Kunden als String, ohne Joins zu verursachen."""
        return (
            f"Kunde(id={self.id}, version={self.version}, "
            f"nachname={self.nachname}, email={self.email}, "
            f"username={self.username})"
        )
