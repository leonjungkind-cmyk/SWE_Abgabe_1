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

"""Anwendungskern für Benutzerdaten."""
from collections.abc import Mapping
from dataclasses import asdict
from typing import Any, Final

from fastapi import Request
from jwcrypto.common import JWException
from keycloak import KeycloakAuthenticationError, KeycloakOpenID
from loguru import logger

from patient.config import keycloak_config
from patient.security.exceptions import AuthorizationError, LoginError
from patient.security.role import Role
from patient.security.user import User

__all__ = ["TokenService"]


class TokenService:
    """Schnittstelle für das Management der Tokens von Keycloak."""

    def __init__(self) -> None:
        """Initialisierung der Schnittstelle zu Keycloak."""
        # double star operator = double asterisk operator:
        # Dictionary auspacken als Schluessel-Wert-Paare
        # -> Namen der Schluessel = Namen der Funktionsargumente
        # https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters
        # https://docs.python.org/3/reference/expressions.html#dictionary-displays
        self.keycloak = KeycloakOpenID(**asdict(keycloak_config))

    def token(self, username: str | None, password: str | None) -> Mapping[str, str]:
        """Zu Benutzername und Passwort werden Access und Refresh Token ermittelt.

        :param username: Benutzername
        :param password: Passwort
        :return: Ein JSON-Datensatz mit Access und Refresh Token sowie Ablaufdatum
        :rtype: [Mapping[str, str]]
        :raises LoginError: Falls Benutzername und/oder Passwort falsch ist
        """
        if username is None or password is None:
            raise LoginError(username=username)

        logger.debug("username={}, password={}", username, password)
        try:
            token = self.keycloak.token(username, password)
        except KeycloakAuthenticationError as err:
            logger.debug("err={}", err)
            raise LoginError(username=username) from err

        logger.debug("token={}", token)
        return token

    def _get_token_from_request(self, request: Request) -> str:
        """Den Token aus "Authorization"-String im Request-Header extrahieren.

        :param request: Request-Objekt von FastAPI mit codiertem "Authorization"-String
                        einschließlich Bearer
        :return: String nach 'Bearer' im Authorization-Header
        :rtype: str
        :raises: AuthorizationError, falls der Authorization_Header syntaktisch falsch
        ist.
        """
        authorization_header: Final = request.headers.get("Authorization")
        logger.debug("authorization_header={}", authorization_header)
        if authorization_header is None:
            raise AuthorizationError
        # JWT nach dem einleitenden Teilstring "Bearer" extrahieren
        try:
            # https://docs.python.org/3/library/stdtypes.html#str.split
            authorization_scheme, bearer_token = authorization_header.split()
        except ValueError as err:
            # keine 2 Teilstrings, die durch Leerzeichen getrennt sind
            raise AuthorizationError from err
        if authorization_scheme.lower() != "bearer":
            raise AuthorizationError
        return bearer_token

    def get_user_from_token(self, token: str) -> User:
        """Die User-Daten aus dem codierten Token extrahieren.

        :param token: Token als String
        :return: User-Daten mit Benutzername und Rollen
        :rtype: User
        :raises AuthorizationError: Falls keine User-Daten extrahiert werden können
        """
        try:
            token_decoded: Final = self.keycloak.decode_token(token=token)
        except (JWException) as err:
            # Oberklasse von InvalidJWSObject, InvalidJWSSignature, JWKeyNotFound
            # Ungueltiger Token, der nicht decodiert werden kann
            raise AuthorizationError from err

        logger.debug("token_decoded={}", token_decoded)
        username: Final[str] = token_decoded["preferred_username"]
        email: Final[str] = token_decoded["email"]
        nachname: Final[str] = token_decoded["family_name"]
        vorname: Final[str] = token_decoded["given_name"]
        roles = self.get_roles_from_token(token_decoded)

        user = User(
            username=username,
            email=email,
            nachname=nachname,
            vorname=vorname,
            roles=roles,
        )
        logger.debug("user={}", user)
        return user

    def get_user_from_request(self, request: Request) -> User:
        """Die User-Daten aus dem codierten "Authorization"-String extrahieren.

        :param request: Request-Objekt von FastAPI mit codiertem "Authorization"-String
                        einschließlich Bearer
        :return: User-Daten mit Benutzername und Rollen
        :rtype: User
        """
        bearer_token: Final = self._get_token_from_request(request)
        user: Final = self.get_user_from_token(token=bearer_token)
        logger.debug("user={}", user)
        return user

    def get_roles_from_token(self, token: str | Mapping[str, Any]) -> list[Role]:
        """Aus einem Access Token von Keycloak die zugehörigen Rollen extrahieren.

        :param token: Zu überprüfender Token
        :return: Liste der Rollen
        :rtype: list[str]
        """
        if isinstance(token, str):
            token_decoded = self.keycloak.decode_token(token=token)
        else:
            token_decoded = token
        logger.debug("token_decoded={}", token_decoded)

        roles: Final[str] = token_decoded["resource_access"][self.keycloak.client_id][
            "roles"
        ]
        roles_enum: Final = [Role[role.upper()] for role in roles]
        logger.debug("roles_enum={}", roles_enum)
        return roles_enum
