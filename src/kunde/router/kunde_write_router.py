"""KundeWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from kunde.problem_details import create_problem_details
from kunde.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from kunde.router.dependencies import get_write_service
from kunde.router.kunde_model import KundeModel
from kunde.router.kunde_update_model import KundeUpdateModel
from kunde.security import Role, RolesRequired
from kunde.service.kunde_write_service import KundeWriteService

__all__ = ["kunde_write_router"]


kunde_write_router: Final = APIRouter(tags=["Schreiben"])


@kunde_write_router.post(
    "",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
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


@kunde_write_router.put(
    "/{kunde_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.kunde]))],
)
def put(
    kunde_id: int,
    kunde_update_model: KundeUpdateModel,
    request: Request,
    service: Annotated[KundeWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen Kunden zu aktualisieren.

    :param kunde_id: ID des zu aktualisierenden Kunden als Pfadparameter
    :param kunde_update_model: Neue Kundedaten
    :param request: Request mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "kunde_id={}, if_match={}, kunde_update_model={}",
        kunde_id,
        if_match_value,
        kunde_update_model,
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
        return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)

    kunde: Final = kunde_update_model.to_kunde()
    kunde_modified: Final = service.update(
        kunde=kunde,
        kunde_id=kunde_id,
        version=version_int,
    )
    logger.debug("kunde_modified={}", kunde_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{kunde_modified.version}"'},
    )


@kunde_write_router.delete(
    "/{kunde_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.kunde]))],
)
def delete_by_id(
    kunde_id: int,
    service: Annotated[KundeWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen Kunden anhand seiner ID zu löschen.

    :param kunde_id: ID des zu löschenden Kunden
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("kunde_id={}", kunde_id)
    service.delete_by_id(kunde_id=kunde_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
