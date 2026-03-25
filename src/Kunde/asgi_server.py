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

"""Funktion `run` für die FastAPI-Applikation mit dem ASGI-Server _uvicorn_."""

from ssl import PROTOCOL_TLS_SERVER

import uvicorn

from patient.config import (
    host_binding,
    port,
    tls_certfile,
    tls_keyfile,
)
from patient.fastapi_app import app  # noqa: F401

__all__ = ["run"]


def run() -> None:
    """Start der Anwendung mit uvicorn."""
    # https://www.uvicorn.org/settings mit folgenden (Default-) Werten
    # host="127.0.0.1"
    # port=8000
    # loop="auto" (default), "asyncio", "uvloop" (nur Linux und MacOS)
    # http="auto" (default), "h11", "httptools" Python Binding fuer HTTP Parser von Node
    # interface="auto" (default), "asgi2", "asgi3", "wsgi"
    uvicorn.run(
        "patient:app",
        loop="asyncio",
        http="h11",
        interface="asgi3",
        host=host_binding,
        port=port,
        ssl_keyfile=tls_keyfile,
        ssl_certfile=tls_certfile,
        # "OpenSSL has deprecated all version specific protocols"
        # https://docs.python.org/3/library/ssl.html#protocol-versions
        ssl_version=PROTOCOL_TLS_SERVER,  # DevSkim: ignore DS440070
    )
