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

"""PatientGetRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from patient.repository import Pageable
from patient.repository.slice import Slice
from patient.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from patient.router.dependencies import get_service
from patient.router.page import Page
from patient.security import Role, RolesRequired, User
from patient.service import PatientDTO, PatientService

__all__ = ["patient_router"]


# APIRouter auf Basis der Klasse Router von Starlette
patient_router: Final = APIRouter(tags=["Lesen"])


@patient_router.get(
    "/{patient_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PATIENT]))],
)
def get_by_id(
    patient_id: int,
    request: Request,
    service: Annotated[PatientService, Depends(get_service)],
) -> Response:
    """Suche mit der Patient-ID.

    :param patient_id: ID des gesuchten Patienten als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit ggf. If-None-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit dem gefundenen Patientendatensatz
    :rtype: Response
    :raises NotFoundError: Falls kein Patient gefunden wurde
    :raises ForbiddenError: Falls die Patientendaten nicht gelesen werden dürfen
    """
    # User-Objekt ist durch Depends(RolesRequired()) in Request.state gepuffert
    user: Final[User] = request.state.current_user
    logger.debug("patient_id={}, user={}", patient_id, user)

    patient: Final = service.find_by_id(patient_id=patient_id, user=user)
    logger.debug("{}", patient)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == patient.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    return JSONResponse(
        content=_patient_to_dict(patient),
        headers={ETAG: f'"{patient.version}"'},
    )


@patient_router.get(
    "",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def get(
    request: Request,
    service: Annotated[PatientService, Depends(get_service)],
) -> JSONResponse:
    """Suche mit Query-Parameter.

    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit Query-Parameter
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit einer Seite mit Patienten-Daten
    :rtype: Response
    :raises NotFoundError: Falls keine Patienten gefunden wurden
    """
    query_params: Final = request.query_params
    log_str: Final = "{}"
    logger.debug(log_str, query_params)

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    suchparameter = dict(query_params)
    if "page" in query_params:
        del suchparameter["page"]
    if "size" in query_params:
        del suchparameter["size"]

    patient_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _patient_slice_to_page(patient_slice, pageable)
    logger.debug(log_str, result)
    return JSONResponse(content=result)


@patient_router.get(
    "/nachnamen/{teil}",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def get_nachnamen(
    teil: str,
    service: Annotated[PatientService, Depends(get_service)],
) -> JSONResponse:
    """Suche Nachnamen zum gegebenen Teilstring.

    :param teil: Teilstring der gefundenen Nachnamen
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 200 und gefundenen Nachnamen im Body
    :rtype: Response
    :raises NotFoundError: Falls keine Nachnamen gefunden wurden
    """
    logger.debug("teil={}", teil)
    nachnamen: Final = service.find_nachnamen(teil=teil)
    return JSONResponse(content=nachnamen)


def _patient_slice_to_page(
    patient_slice: Slice[PatientDTO],
    pageable: Pageable,
) -> dict[str, Any]:
    patient_dict: Final = tuple(
        _patient_to_dict(patient) for patient in patient_slice.content
    )
    page: Final = Page.create(
        content=patient_dict,
        pageable=pageable,
        total_elements=patient_slice.total_elements,
    )
    return asdict(obj=page)


def _patient_to_dict(patient: PatientDTO) -> dict[str, Any]:
    # https://docs.python.org/3/library/dataclasses.html
    patient_dict: Final = asdict(obj=patient)
    patient_dict.pop("version")
    patient_dict.update({"geburtsdatum": patient.geburtsdatum.isoformat()})
    return patient_dict
