"""Modul für den Geschäftslogik."""

from patient.service.adresse_dto import AdresseDTO
from patient.service.exceptions import (
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from patient.service.mailer import send_mail
from patient.service.patient_dto import PatientDTO
from patient.service.patient_service import PatientService
from patient.service.patient_write_service import PatientWriteService

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "AdresseDTO",
    "EmailExistsError",
    "ForbiddenError",
    "NotFoundError",
    "PatientDTO",
    "PatientService",
    "PatientWriteService",
    "UsernameExistsError",
    "VersionOutdatedError",
    "send_mail",
]
