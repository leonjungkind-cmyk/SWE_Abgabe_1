"""Data class für die Login-Daten."""

from dataclasses import dataclass

__all__ = ["LoginData"]


@dataclass
class LoginData:
    """Data class für die Login-Daten."""

    username: str
    """Benutzername"""

    password: str
    """Passwort"""

    class Config:
        """Beispiel für OpenAPI."""

        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "p",  # NOSONAR
            },
        }
