"""Enum für Rollen."""

from enum import StrEnum


class Role(StrEnum):
    """Enum für Rollen."""

    ADMIN = "admin"
    """Rolle für die Administration."""

    kunde = "kunde"
    """Rolle registrierter Kunde."""
