"""Entity-Klasse für die Adresse."""

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.base import Base


class Adresse(Base):
    """Entity-Klasse für die Adresse."""

    __tablename__ = "adresse"

    strasse: Mapped[str]
    """Die Straße."""

    hausnummer: Mapped[str]
    """Die Hausnummer."""

    plz: Mapped[str]
    """Die Postleitzahl."""

    ort: Mapped[str]
    """Der Ort."""

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID."""

    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"), unique=True)
    """ID des zugehörigen Kunden als Fremdschlüssel."""

    kunde: Mapped[Kunde] = relationship(  # noqa: F821 # ty: ignore[unresolved-reference] # pyright: ignore[reportUndefinedVariable]
        back_populates="adresse",
    )
    """Das zugehörige transiente Kunde-Objekt."""

    def __repr__(self) -> str:
        """Ausgabe einer Adresse als String ohne die Kundendaten."""
        return (
            f"Adresse(id={self.id}, strasse={self.strasse}, "
            f"hausnummer={self.hausnummer}, plz={self.plz}, ort={self.ort})"
        )
