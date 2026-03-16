# Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Konfiguration für _python-keycloak_ zum Zugriff auf _Keycloak_."""

from dataclasses import dataclass
from typing import Final

from loguru import logger

from patient.config.config import app_config

__all__ = [
    "csv_config",
    "keycloak_admin_config",
    "keycloak_config",
]


@dataclass(eq=False, slots=True, kw_only=True)
class KeycloakConfig:
    """Allgemeine Konfigurationsdaten für Keycloak."""

    server_url: str
    realm_name: str
    client_id: str
    client_secret_key: str
    verify: bool = False


@dataclass(eq=False, slots=True, kw_only=True)
class KeycloakAdminConfig(KeycloakConfig):
    """Konfigurationsdaten für die Keycloak-Administration."""

    username: str
    password: str


_keycloak_toml: Final = app_config.get("keycloak", {})

_schema: Final = _keycloak_toml.get("schema", "https")
_host: Final[str] = _keycloak_toml.get("host", "keycloak")
_port: Final[int] = _keycloak_toml.get("port", 8443)
_url: Final = f"{_schema}://{_host}:{_port}/"  # DevSkim: ignore DS137138
_management_port: Final[int] = _keycloak_toml.get("management-port", 9000)
_keycloak_management_url: Final = f"{_schema}://{_host}:{_management_port}"

_realm: Final[str] = _keycloak_toml.get("realm", "python")
_client_id: Final[str] = _keycloak_toml.get("client-id", "python-client")
_client_secret: Final[str] = _keycloak_toml.get("client-secret")

keycloak_config = KeycloakConfig(
    server_url=_url,
    realm_name=_realm,
    client_id=_client_id,
    client_secret_key=_client_secret,
    verify=False,
)
"""Administrations-Schnittstelle zu Keycloak durch _python-keycloak_."""

logger.debug("keycloak: keycloak_config={}", keycloak_config)

csv_config: Final = _keycloak_toml.get("csv", "/csv/patient.csv")
logger.debug("keycloak: csv={}", csv_config)


_admin: Final[str] = _keycloak_toml.get("admin", "admin")
_admin_password: Final[str] = _keycloak_toml.get("admin-password")
logger.debug("keycloak admin: username={}, password={}", _admin, _admin_password)
keycloak_admin_config = KeycloakAdminConfig(
    server_url=_url,
    username=_admin,
    password=_admin_password,
    realm_name=_realm,
    client_id=_client_id,
    client_secret_key=_client_secret,
    verify=False,
)
"""Administrations-Schnittstelle zu Keycloak durch _python-keycloak_."""
