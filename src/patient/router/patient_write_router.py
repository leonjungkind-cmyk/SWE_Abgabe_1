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

"""PatientWriteRouter."""
from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from patient.problem_details import create_problem_details
from patient.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from patient.router.dependencies import get_write_service
from patient.router.patient_model import PatientModel
from patient.router.patient_update_model import PatientUpdateModel
from patient.security import Role, RolesRequired
from patient.service import PatientWriteService

__all__ = ["patient_write_router"]


patient_write_router: Final = APIRouter(tags=["Schreiben"])


@patient_write_router.post("")
def post(
    patient_model: PatientModel,
    request: Request,
    service: Annotated[PatientWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Patienten anzulegen.

    :param patient_model: Patientendaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    :raises UsernameExistsError: Falls der Benutzername bereits existiert
    """
    logger.debug("patient_model={}", patient_model)
    patient_dto: Final = service.create(patient=patient_model.to_patient())
    logger.debug("patient_dto={}", patient_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{patient_dto.id}"},
    )


@patient_write_router.put(
    "/{patient_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PATIENT]))],
)
def put(
    patient_id: int,
    patient_update_model: PatientUpdateModel,
    request: Request,
    service: Annotated[PatientWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen Patienten zu aktualisieren.

    :param patient_id: ID des zu aktualisierenden Patienten als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises ValidationError: Falls es bei Marshmallow Validierungsfehler gibt
    :raises EmailExistsError: Falls die neue Emailadresse bereits
    :raises NotFoundError: Falls zur id kein Patient existiert
    :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "patient_id={}, if_match={}, patient_update_model={}",
        patient_id,
        if_match_value,
        patient_update_model,
    )

    if if_match_value is None:
        return create_problem_details(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        )

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return create_problem_details(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return Response(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    patient: Final = patient_update_model.to_patient()
    patient_modified: Final = service.update(
        patient=patient,
        patient_id=patient_id,
        version=version_int,
    )
    logger.debug("patient_modified={}", patient_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{patient_modified.version}"'},
    )


@patient_write_router.delete(
    "/{patient_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PATIENT]))],
)
def delete_by_id(
    patient_id: int,
    service: Annotated[PatientWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen Patienten anhand seiner ID zu löschen.

    :param patient_id: ID des zu löschenden Patienten
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("patient_id={}", patient_id)
    service.delete_by_id(patient_id=patient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
