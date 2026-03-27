"""Modul für den Geschäftslogik."""

from kunde.service.adresse_dto import AdresseDTO
from kunde.service.exceptions import (
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from kunde.service.mailer import send_mail
from kunde.service.kunde_dto import KundeDTO
from kunde.service.kunde_service import KundeService
from kunde.service.kunde_write_service import KundeWriteService

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "AdresseDTO",
    "EmailExistsError",
    "ForbiddenError",
    "NotFoundError",
    "KundeDTO",
    "KundeService",
    "KundeWriteService",
    "UsernameExistsError",
    "VersionOutdatedError",
    "send_mail",
]
