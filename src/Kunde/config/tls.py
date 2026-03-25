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

"""Konfiguration für den privaten Schlüssel und das Zertifikat für TLS."""

from importlib.resources import files
from typing import TYPE_CHECKING, Final

from loguru import logger

from patient.config.config import app_config, resources_path

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

__all__ = ["tls_certfile", "tls_keyfile"]


_tls_toml: Final = app_config.get("tls", {})
_tls_path: Final[Traversable] = files(resources_path) / "tls"

_key: Final[str] = _tls_toml.get("key", "key.pem")
tls_keyfile: Final[str] = str(_tls_path / _key)
logger.debug("private keyfile TLS: {}", tls_keyfile)

_certificate: Final[str] = _tls_toml.get("certificate", "certificate.crt")
tls_certfile: Final[str] = str(_tls_path / _certificate)
logger.debug("certfile TLS: {}", tls_certfile)
