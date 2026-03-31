"""Repository-Paket für Kunde."""

from kunde.repository.kunde_repository import KundeRepository
from kunde.repository.session_factory import Session

__all__ = ["KundeRepository", "Session"]
