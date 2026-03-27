"""Modul für den DB-Zugriff."""

from kunde.repository.pageable import MAX_PAGE_SIZE, Pageable
from kunde.repository.kunde_repository import KundeRepository
from kunde.repository.session_factory import Session, engine
from kunde.repository.slice import Slice

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "MAX_PAGE_SIZE",
    "Pageable",
    "KundeRepository",
    "Session",
    "Slice",
    "engine",
]
