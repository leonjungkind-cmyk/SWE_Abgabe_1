"""DTO für Kundendaten."""

from kunde.entity.kunde import Kunde

__all__ = ["KundeDTO"]


class KundeDTO:
    """DTO-Klasse für einen Kunden."""

    def __init__(self, kunde: Kunde) -> None:
        """Initialisierung mit einer Kunde-Entity.

        :param kunde: Persistierter Kunde
        """
        self.id = kunde.id
        self.nachname = kunde.nachname
        self.email = kunde.email

    def __repr__(self) -> str:
        """String-Darstellung des DTO.

        :return: String-Repräsentation
        :rtype: str
        """
        return (
            f"KundeDTO(id={self.id}, nachname={self.nachname}, email={self.email})"
        )
