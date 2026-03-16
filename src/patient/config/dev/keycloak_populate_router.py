# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""DbPopulateController."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from loguru import logger

from patient.config.dev.keycloak_populate import (
    KeycloakPopulateService,
    get_keycloak_populate_service,
)
from patient.security import Role, RolesRequired, User

__all__ = ["router"]


router: Final = APIRouter()


# "Dependency Injection" durch Depends
@router.post(
    "/keycloak_populate",
    tags=["Admin"],
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def populate(
    request: Request,
    service: Annotated[KeycloakPopulateService, Depends(get_keycloak_populate_service)],
) -> JSONResponse:
    """Keycloak mit Testdaten durch einen POST-Request neu zu laden.

    :return: JSON-Datensatz mit der Erfolgsmeldung
    :rtype: dict[str, str]
    """
    current_user: Final[User] = request.state.current_user
    logger.warning(
        'REST-Schnittstelle zum Neuladen von Keycloak aufgerufen von "{}"',
        current_user.username,
    )
    service.populate()
    return JSONResponse(content={"keycloak_populate": "success"})
