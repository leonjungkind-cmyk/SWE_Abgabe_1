"""KundeReadRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice
from kunde.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from kunde.router.dependencies import get_read_service
from kunde.router.page import Page
from kunde.service import KundeReadService
from kunde.service.kunde_dto import KundeDTO

__all__ = ["kunde_read_router"]

kunde_read_router: Final = APIRouter(tags=["Lesen"])


@kunde_read_router.get(
    "/{kunde_id}",
)
def get_by_id(
    kunde_id: int,
    request: Request,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> Response:
    """Suche mit der Kunden-ID.

    :param kunde_id: ID des gesuchten Kunden als Pfadparameter
    :param request: Injiziertes Request-Objekt mit ggf. If-None-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit dem gefundenen Kundendatensatz
    :rtype: Response
    :raises NotFoundError: Falls kein Kunde gefunden wurde
    """
    logger.debug("kunde_id={}", kunde_id)

    kunde: Final = service.find_by_id(kunde_id=kunde_id)
    logger.debug("{}", kunde)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        try:
            if int(version) == kunde.version:
                return Response(status_code=status.HTTP_304_NOT_MODIFIED)
        except ValueError:
            logger.debug("invalid version={}", version)

    return JSONResponse(
        content=_kunde_to_dict(kunde),
        headers={ETAG: f'"{kunde.version}"'},
    )


@kunde_read_router.get(
    "",
)
def get(
    request: Request,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> JSONResponse:
    """Suche mit Query-Parametern.

    :param request: Injiziertes Request-Objekt mit Query-Parametern
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit einer Seite von Kundendaten
    :rtype: JSONResponse
    :raises NotFoundError: Falls keine Kunden gefunden wurden
    """
    query_params: Final = request.query_params
    logger.debug("{}", query_params)

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    suchparameter = dict(query_params)
    suchparameter.pop("page", None)
    suchparameter.pop("size", None)

    kunde_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _kunde_slice_to_page(kunde_slice, pageable)
    logger.debug("{}", result)
    return JSONResponse(content=result)


@kunde_read_router.get(
    "/nachnamen/{teil}",
)
def get_nachnamen(
    teil: str,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> JSONResponse:
    """Suche Nachnamen zum gegebenen Teilstring.

    :param teil: Teilstring der gesuchten Nachnamen
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit den gefundenen Nachnamen
    :rtype: JSONResponse
    :raises NotFoundError: Falls keine Nachnamen gefunden wurden
    """
    logger.debug("teil={}", teil)
    nachnamen: Final = service.find_nachnamen(teil=teil)
    return JSONResponse(content=nachnamen)


def _kunde_slice_to_page(
    kunde_slice: Slice[KundeDTO],
    pageable: Pageable,
) -> dict[str, Any]:
    kunde_dicts: Final = tuple(_kunde_to_dict(k) for k in kunde_slice.content)
    page: Final = Page.create(
        content=kunde_dicts,
        pageable=pageable,
        total_elements=kunde_slice.total_elements,
    )
    return asdict(obj=page)


def _kunde_to_dict(kunde: KundeDTO) -> dict[str, Any]:
    return {
        "id": kunde.id,
        "nachname": kunde.nachname,
        "email": kunde.email,
        "adresse": {
            "plz": kunde.adresse.plz,
            "ort": kunde.adresse.ort,
        },
        "bestellungen": [
            {"produktname": b.produktname, "menge": b.menge} for b in kunde.bestellungen
        ],
    }
