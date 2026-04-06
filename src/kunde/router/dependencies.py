"""Abhängigkeiten für die Router."""

from kunde.repository import KundeRepository
from kunde.service.kunde_read_service import KundeReadService
from kunde.service.kunde_write_service import KundeWriteService


def get_write_service() -> KundeWriteService:
    """Erzeuge den Write-Service für Kunde.

    :return: Instanz von KundeWriteService
    :rtype: KundeWriteService
    """
    repo = KundeRepository()
    return KundeWriteService(repo)


def get_read_service() -> KundeReadService:
    """Erzeuge den Read-Service für Kunde.

    :return: Instanz von KundeReadService
    :rtype: KundeReadService
    """
    repo = KundeRepository()
    return KundeReadService(repo)


def get_service() -> KundeReadService:
    """Kompatibilitaets-Alias fuer bestehenden Code."""
    return get_read_service()
