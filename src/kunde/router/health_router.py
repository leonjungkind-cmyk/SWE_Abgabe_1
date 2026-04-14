"""Health-Check-Endpunkte zur Prüfung von Verfügbarkeit und Datenbankverbindung."""

from typing import Final

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import text

from kunde.repository import engine

__all__ = ["health_router"]

health_router: Final = APIRouter(tags=["Health"])


@health_router.get("/liveness")
def liveness() -> JSONResponse:
    """Prüft, ob der Server läuft.

    :return: JSON mit status=up
    :rtype: JSONResponse
    """
    return JSONResponse(content={"status": "up"})


@health_router.get("/readiness")
def readiness() -> JSONResponse:
    """Prüft, ob die Datenbankverbindung bereit ist.

    :return: JSON mit db=up oder db=down
    :rtype: JSONResponse
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.debug("Datenbankverbindung OK")
        return JSONResponse(content={"db": "up"})
    except Exception:  # noqa: BLE001
        logger.error("Datenbankverbindung nicht verfügbar")
        return JSONResponse(content={"db": "down"}, status_code=503)
