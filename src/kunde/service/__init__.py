"""Service-Paket für Kunde."""

from kunde.service.kunde_read_service import KundeReadService
from kunde.service.kunde_write_service import KundeWriteService

__all__ = ["KundeReadService", "KundeWriteService"]
