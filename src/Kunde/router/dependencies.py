# Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Factory-Funktionen für Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from patient.repository.patient_repository import PatientRepository
from patient.security.dependencies import get_user_service
from patient.security.user_service import UserService
from patient.service.patient_service import PatientService
from patient.service.patient_write_service import PatientWriteService


def get_repository() -> PatientRepository:
    """Factory-Funktion für PatientRepository.

    :return: Das Repository
    :rtype: PatientRepository
    """
    return PatientRepository()


def get_service(
    repo: Annotated[PatientRepository, Depends(get_repository)],
) -> PatientService:
    """Factory-Funktion für PatientService."""
    return PatientService(repo=repo)


def get_write_service(
    repo: Annotated[PatientRepository, Depends(get_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> PatientWriteService:
    """Factory-Funktion für PatientWriteService."""
    return PatientWriteService(repo=repo, user_service=user_service)
