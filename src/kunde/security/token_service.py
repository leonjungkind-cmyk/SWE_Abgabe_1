"""Anwendungskern für Benutzerdaten."""

from collections.abc import Mapping
from dataclasses import asdict
from typing import Any, Final

from fastapi import Request
from jwcrypto.common import JWException
from keycloak import KeycloakAuthenticationError, KeycloakOpenID
from loguru import logger

from kunde.config import keycloak_config
from kunde.security.exceptions import AuthorizationError, LoginError
from kunde.security.role import Role
from kunde.security.user import User

__all__ = ["TokenService"]


class TokenService:
    """Schnittstelle für das Management der Tokens von Keycloak."""

    def __init__(self) -> None:
        """Initialisierung der Schnittstelle zu Keycloak."""
        self.keycloak = KeycloakOpenID(**asdict(keycloak_config))

    def token(self, username: str | None, password: str | None) -> Mapping[str, str]:
        """Zu Benutzername und Passwort werden Access und Refresh Token ermittelt."""
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
        """Den Token aus "Authorization"-String im Request-Header extrahieren."""
        authorization_header: Final = request.headers.get("Authorization")
        logger.debug("authorization_header={}", authorization_header)

        if authorization_header is None:
            raise AuthorizationError

        try:
            authorization_scheme, bearer_token = authorization_header.split()
        except ValueError as err:
            raise AuthorizationError from err

        if authorization_scheme.lower() != "bearer":
            raise AuthorizationError

        return bearer_token

    def _map_role_name(self, role_name: str) -> Role:
        """Keycloak-Rollenname auf Role-Enum abbilden."""
        normalized = role_name.strip().lower()

        if normalized == "admin":
            return Role.ADMIN
        if normalized == "kunde":
            return Role.kunde

        raise AuthorizationError

    def get_user_from_token(self, token: str) -> User:
        """Die User-Daten aus dem codierten Token extrahieren."""
        try:
            token_decoded: Final = self.keycloak.decode_token(token=token)
        except JWException as err:
            raise AuthorizationError from err

        logger.debug("token_decoded={}", token_decoded)

        username: Final[str] = token_decoded["preferred_username"]
        email: Final[str] = token_decoded["email"]
        nachname: Final[str] = token_decoded.get("family_name", "")
        vorname: Final[str] = token_decoded.get("given_name", "")
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
        """Die User-Daten aus dem codierten Authorization-Header extrahieren."""
        bearer_token: Final = self._get_token_from_request(request)
        user: Final = self.get_user_from_token(token=bearer_token)
        logger.debug("user={}", user)
        return user

    def get_roles_from_token(self, token: str | Mapping[str, Any]) -> list[Role]:
        """Aus einem Access Token von Keycloak die zugehörigen Rollen extrahieren."""
        if isinstance(token, str):
            token_decoded = self.keycloak.decode_token(token=token)
        else:
            token_decoded = token

        logger.debug("token_decoded={}", token_decoded)

        role_names: Final = token_decoded["resource_access"][self.keycloak.client_id][
            "roles"
        ]
        roles_enum: Final = [self._map_role_name(role_name) for role_name in role_names]
        logger.debug("roles_enum={}", roles_enum)
        return roles_enum
