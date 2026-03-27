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

from kunde.repository.kunde_repository import KundeRepository
from kunde.security.dependencies import get_user_service
from kunde.security.user_service import UserService
from kunde.service.kunde_service import KundeService
from kunde.service.kunde_write_service import KundeWriteService


def get_repository() -> KundeRepository:
    """Factory-Funktion für KundeRepository.

    :return: Das Repository
    :rtype: KundeRepository
    """
    return KundeRepository()


def get_service(
    repo: Annotated[KundeRepository, Depends(get_repository)],
) -> KundeService:
    """Factory-Funktion für KundeService."""
    return KundeService(repo=repo)


def get_write_service(
    repo: Annotated[KundeRepository, Depends(get_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> KundeWriteService:
    """Factory-Funktion für KundeWriteService."""
    return KundeWriteService(repo=repo, user_service=user_service)
