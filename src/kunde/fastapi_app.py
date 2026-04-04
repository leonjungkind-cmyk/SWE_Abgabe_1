# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License.

"""MainApp."""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from time import time
from typing import Final

from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from loguru import logger

from kunde.banner import banner
from kunde.repository import engine
from kunde.router.kunde_read_router import kunde_read_router
from kunde.router.kunde_write_router import kunde_write_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: RUF029
    """Banner ausgeben und beim Shutdown die DB-Verbindungen schließen.

    :param app: FastAPI-Anwendung
    """
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
    logger.debug("{} '{}'", request.method, request.url)
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
        "Response time: {:.2f} ms, statuscode: {}",
        duration_ms,
        response.status_code,
    )
    return response


app.include_router(kunde_read_router, prefix="/rest")
app.include_router(kunde_write_router, prefix="/rest")


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
