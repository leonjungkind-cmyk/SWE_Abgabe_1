"""KundeReadRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from loguru import logger

from kunde.router.dependencies import get_read_service
from kunde.service import KundeReadService

__all__ = ["kunde_read_router"]

kunde_read_router: Final = APIRouter(prefix="/kunden", tags=["Lesen"])


@kunde_read_router.get("/{kunde_id}")
def get_by_id(
    kunde_id: int,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> Response:
    logger.debug("kunde_id={}", kunde_id)
    kunde: Final = service.find_by_id(kunde_id=kunde_id)

    if kunde is None:
        return Response(status_code=404)

    return JSONResponse(content={
        "id": kunde.id,
        "nachname": kunde.nachname,
        "email": kunde.email,
    })
