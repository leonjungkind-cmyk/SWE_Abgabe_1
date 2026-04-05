"""Exceptions in der Geschäftslogik."""

from collections.abc import Mapping

__all__ = [
    "EmailExistsError",
    "NotFoundError",
    "VersionOutdatedError",
]


class EmailExistsError(Exception):
    """Exception, falls die Emailadresse bereits vergeben ist."""

    def __init__(self, email: str) -> None:
        """Initialisierung mit der bereits vorhandenen Emailadresse.

        :param email: Bereits existierende Emailadresse
        """
        super().__init__(f"Existierende Email: {email}")
        self.email = email


class NotFoundError(Exception):
    """Exception, falls kein Kunde gefunden wurde."""

    def __init__(
        self,
        kunde_id: int | None = None,
        suchparameter: Mapping[str, str] | None = None,
    ) -> None:
        """Initialisierung mit ID oder Suchparametern, zu denen nichts gefunden wurde.

        :param kunde_id: Kunden-ID, zu der kein Treffer existiert
        :param suchparameter: Filterkriterien, zu denen keine Kunden gefunden wurden
        """
        super().__init__("Not Found")
        self.kunde_id = kunde_id
        self.suchparameter = suchparameter


class VersionOutdatedError(Exception):
    """Exception, falls die Versionsnummer beim Aktualisieren überholt ist."""

    def __init__(self, version: int) -> None:
        """Initialisierung mit der veralteten Versionsnummer.

        :param version: Versionsnummer, die nicht mehr aktuell ist
        """
        super().__init__(f"Veraltete Version: {version}")
        self.version = version
