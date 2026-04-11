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
from kunde.config.dev.keycloak_populate import keycloak_populate
from kunde.config.dev.keycloak_populate_router import (
    router as keycloak_populate_router,
)
from kunde.config.dev_modus import dev_db_populate, dev_keycloak_populate
from kunde.problem_details import create_problem_details
from kunde.repository import engine
from kunde.graphql_api import graphql_router as gql_router
from kunde.router.kunde_read_router import kunde_read_router
from kunde.router.kunde_write_router import kunde_write_router
from kunde.security import AuthorizationError, LoginError
from kunde.security.auth_router import router as auth_router
from kunde.security.response_headers import set_response_headers
from kunde.service.exceptions import (
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    VersionOutdatedError,
)

__all__ = [
    "authorization_error_handler",
    "email_exists_error_handler",
    "forbidden_error_handler",
    "login_error_handler",
    "not_found_error_handler",
    "version_outdated_error_handler",
]


# --------------------------------------------------------------------------------------
# S t a r t u p   u n d   S h u t d o w n
# --------------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: RUF029
    """DB und Keycloak neu laden, falls im dev-Modus, sowie Banner in der Konsole."""
    if dev_db_populate:
        db_populate()
    if dev_keycloak_populate:
        keycloak_populate()
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
# S e c u r i t y
# --------------------------------------------------------------------------------------
@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Header-Daten beim Response für IT-Sicherheit setzen.

    :param request: Aktueller HTTP-Request
    :param call_next: Nächste Middleware bzw. eigentlicher Handler
    :return: HTTP-Response mit zusätzlichen Security-Headern
    :rtype: Response
    """
    response: Final[Response] = await call_next(request)
    set_response_headers(response)
    return response


# --------------------------------------------------------------------------------------
# R E S T
# --------------------------------------------------------------------------------------
app.include_router(kunde_read_router, prefix="/rest/kunden")
app.include_router(kunde_write_router, prefix="/rest")
app.include_router(gql_router, prefix="/graphql")

if dev_db_populate:
    app.include_router(db_populate_router, prefix="/dev")

if dev_keycloak_populate:
    app.include_router(keycloak_populate_router, prefix="/dev")


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


@app.exception_handler(ForbiddenError)
def forbidden_error_handler(_request: Request, _err: ForbiddenError) -> Response:
    """Exception-Handling für ForbiddenError.

    :param _err: Exception, falls der Zugriff nicht erlaubt ist
    :return: Response mit Statuscode 403
    :rtype: Response
    """
    return create_problem_details(status_code=status.HTTP_403_FORBIDDEN)


@app.exception_handler(AuthorizationError)
def authorization_error_handler(
    _request: Request,
    _err: AuthorizationError,
) -> Response:
    """Exception-Handling für AuthorizationError.

    :param _err: Exception bei fehlendem oder ungültigem Authorization-Header
    :return: Response mit Statuscode 401
    :rtype: Response
    """
    return create_problem_details(status_code=status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(LoginError)
def login_error_handler(_request: Request, err: LoginError) -> Response:
    """Exception-Handling für LoginError.

    :param err: Exception bei fehlerhaftem Benutzername oder Passwort
    :return: Response mit Statuscode 401
    :rtype: Response
    """
    return create_problem_details(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=str(err),
    )


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


@app.exception_handler(VersionOutdatedError)
def version_outdated_error_handler(
    _request: Request,
    err: VersionOutdatedError,
) -> Response:
    """Exception-Handling für VersionOutdatedError.

    :param err: Exception, falls die Versionsnummer veraltet ist
    :return: Response mit Statuscode 412
    :rtype: Response
    """
    return create_problem_details(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        detail=str(err),
    )
