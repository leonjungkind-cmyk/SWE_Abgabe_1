"""Entity-Klasse für Benutzerdaten."""

from dataclasses import dataclass

from kunde.security.role import Role


@dataclass()
class User:
    """Entity-Klasse für Benutzerdaten."""

    username: str
    """Benutzername."""

    email: str
    """Emailadresse."""

    nachname: str
    """Nachname."""

    vorname: str
    """Vorname."""

    roles: list[Role]
    """Rollen als Liste von Enums."""

    password: str | None = None
    """Passwort."""
