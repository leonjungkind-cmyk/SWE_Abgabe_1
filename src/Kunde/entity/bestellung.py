"""Entity-Klasse für Bestellung."""

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.base import Base


class Bestellung(Base):
    """Entity-Klasse für Bestellung."""

    __tablename__ = "bestellung"

    produktname: Mapped[str]
    """Der Name des Produkts."""

    menge: Mapped[int]
    """Die bestellte Menge."""

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID."""

    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"))
    """ID des zugehörigen Kunden als Fremdschlüssel."""

    kunde: Mapped[Kunde] = relationship(  # noqa: F821 # ty: ignore[unresolved-reference] # pyright: ignore[reportUndefinedVariable]
        back_populates="bestellungen",
    )
    """Das zugehörige transiente Kunde-Objekt."""

    def __repr__(self) -> str:
        """Ausgabe der Bestellung als String ohne die Kundendaten."""
        return (
            f"Bestellung(id={self.id}, produktname={self.produktname}, "
            f"menge={self.menge})"
        )
