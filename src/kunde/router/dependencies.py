"""Abhängigkeiten für die Router."""

from kunde.repository import KundeRepository
from kunde.service.kunde_write_service import KundeWriteService


def get_write_service() -> KundeWriteService:
    """Erzeuge den Write-Service für Kunde.

    :return: Instanz von KundeWriteService
    :rtype: KundeWriteService
    """
    repo = KundeRepository()
    return KundeWriteService(repo)
