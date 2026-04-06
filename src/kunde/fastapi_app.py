"""MainApp."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from time import time
from typing import Final

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from loguru import logger

from kunde.banner import banner
from kunde.config.dev.db_populate import db_populate
from kunde.config.dev.db_populate_router import router as db_populate_router
from kunde.config.dev_modus import dev_db_populate, dev_keycloak_populate
from kunde.problem_details import create_problem_details
from kunde.repository import engine
from kunde.router.kunde_read_router import kunde_read_router
from kunde.router.kunde_write_router import kunde_write_router
from kunde.service.exceptions import EmailExistsError, NotFoundError

__all__ = [
    "email_exists_error_handler",
    "not_found_error_handler",
]


# --------------------------------------------------------------------------------------
# S t a r t u p   u n d   S h u t d o w n
# --------------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: RUF029
    """DB neu laden, falls im dev-Modus, sowie Banner in der Konsole."""
    if dev_db_populate:
        db_populate()
    banner(app.routes)
    yield
    logger.info("Der Server wird heruntergefahren.")
    logger.info("Connection-Pool fuer die DB wird getrennt.")
    engine.dispose()


app: Final = FastAPI(lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=500)


@app.middleware("http")
async def log_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """HTTP-Request protokollieren.

    :param request: Aktueller HTTP-Request
    :param call_next: Nächste Middleware bzw. eigentlicher Handler
    :return: HTTP-Response
    :rtype: Response
    """
    logger.debug(f"{request.method} '{request.url}'")
    return await call_next(request)


@app.middleware("http")
async def log_response_time(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Bearbeitungszeit eines Requests protokollieren.

    :param request: Aktueller HTTP-Request
    :param call_next: Nächste Middleware bzw. eigentlicher Handler
    :return: HTTP-Response
    :rtype: Response
    """
    start = time()
    response = await call_next(request)
    duration_ms = (time() - start) * 1000
    logger.debug(
        f"Response time: {duration_ms:.2f} ms, "
        f"statuscode: {response.status_code}"
    )
    return response


# --------------------------------------------------------------------------------------
# R E S T
# --------------------------------------------------------------------------------------
app.include_router(kunde_read_router, prefix="/rest/kunden")
app.include_router(kunde_write_router, prefix="/rest")

if dev_db_populate:
    app.include_router(db_populate_router, prefix="/dev")

if dev_keycloak_populate:
    pass  # wird ergänzt, sobald das Security-Modul vorhanden ist


# --------------------------------------------------------------------------------------
# F a v i c o n
# --------------------------------------------------------------------------------------
@app.get("/favicon.ico")
def favicon() -> FileResponse:
    """favicon.ico bereitstellen.

    :return: Response-Objekt mit favicon.ico
    :rtype: FileResponse
    """
    src_path: Final = Path("src")
    file_name: Final = "favicon.ico"
    favicon_path: Final = Path("kunde") / "static" / file_name
    file_path: Final = src_path / favicon_path if src_path.is_dir() else favicon_path
    logger.debug("file_path={}", file_path)
    return FileResponse(
        path=file_path,
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


# --------------------------------------------------------------------------------------
# E x c e p t i o n   H a n d l e r
# --------------------------------------------------------------------------------------
@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, _err: NotFoundError) -> Response:
    """Exception-Handling für NotFoundError.

    :param _err: Exception, falls kein Kunde gefunden wurde
    :return: Response mit Statuscode 404
    :rtype: Response
    """
    return create_problem_details(status_code=status.HTTP_404_NOT_FOUND)


@app.exception_handler(EmailExistsError)
def email_exists_error_handler(_request: Request, err: EmailExistsError) -> Response:
    """Exception-Handling für EmailExistsError.

    :param err: Exception, falls die Emailadresse des neuen Kunden bereits existiert
    :return: Response mit Statuscode 422
    :rtype: Response
    """
    return create_problem_details(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(err),
    )
