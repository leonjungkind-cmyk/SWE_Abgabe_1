# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Konfiguration für ASGI."""

from typing import Final

from patient.config.config import app_config

__all__ = ["host_binding", "port"]


_server_toml: Final = app_config.get("server", {})

host_binding: Final[str] = _server_toml.get("host-binding", "127.0.0.1")
"""'Host Binding', z.B. 127.0.0.1 (default) oder 0.0.0.0."""

port: Final[int] = _server_toml.get("port", 8000)
"""Port für den Server (default: 8000)."""

reload: Final[bool] = bool(_server_toml.get("reload", False))
