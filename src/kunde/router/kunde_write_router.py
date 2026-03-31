# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""KundeWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from kunde.router.dependencies import get_write_service
from kunde.router.kunde_model import KundeModel
from kunde.service.kunde_write_service import KundeWriteService

__all__ = ["kunde_write_router"]


kunde_write_router: Final = APIRouter(tags=["Schreiben"])


@kunde_write_router.post("")
def post(
    kunde_model: KundeModel,
    request: Request,
    service: Annotated[KundeWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Kunden anzulegen.

    :param kunde_model: Kundendaten als Pydantic-Modell
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 201 und Location-Header
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    """
    logger.debug("kunde_model={}", kunde_model)
    kunde_dto: Final = service.create(kunde=kunde_model.to_kunde())
    logger.debug("kunde_dto={}", kunde_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{kunde_dto.id}"},
    )
