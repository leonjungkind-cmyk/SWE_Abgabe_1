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

"""Management der Benutzerdaten mit dem REST-API von Keycloak."""

# https://www.keycloak.org/docs-api/latest/rest-api

from dataclasses import asdict
from typing import Any, Final, cast

from keycloak import KeycloakAdmin, KeycloakConnectionError
from loguru import logger
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from kunde.config import keycloak_admin_config
from kunde.security.role import Role
from kunde.security.user import User

__all__ = ["UserService"]


class UserService:
    """Schnittstelle für das Management der Benutzerdaten von Keycloak."""

    def __init__(self) -> None:
        """Initialisierung der Administrations-Schnittstelle zu Keycloak."""
        # double star operator = double asterisk operator:
        # Dictionary auspacken als Schluessel-Wert-Paare
        # -> Namen der Schluessel = Namen der Funktionsargumente
        # https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters
        # https://docs.python.org/3/reference/expressions.html#dictionary-displays
        self.keycloak_admin = KeycloakAdmin(**asdict(keycloak_admin_config))

        disable_warnings(InsecureRequestWarning)
        try:
            # UUID fuer KeycloakAdmin.assign_client_role()
            self.client_uuid: str = cast(
                "str",
                self.keycloak_admin.get_client_id(keycloak_admin_config.client_id),
            )
            logger.debug("client_id={} für 'python-client'", self.client_uuid)
            roles = self.keycloak_admin.get_client_roles(client_id=self.client_uuid)
            roles_kunde = [role for role in roles if role["name"] == "kunde"]
            # Rolle 'kunde' in Keycloak fuer KeycloakAdmin.assign_client_role() und
            # ist ein dict mit Schluesseln "id", "name", "description", ...
            self.rolle_kunde = roles_kunde[0]
            logger.debug("rolle_kunde={}", self.rolle_kunde)
        except KeycloakConnectionError:
            logger.error("Keine Verbindung zu Keycloak! Ist Keycloak gestartet?")
            self.client_uuid = "N/A"
            self.rolle_kunde = None

    def username_exists(self, username: str) -> bool:
        """Abfrage, ob ein Benutzername bereits existiert.

        :param username: Der zu überprüfende Benutzername
        :return: True, falls der Benutzername bereits existiert, False sonst
        :rtype: bool
        :raises KeycloakError: Falls mit Keycloak ein Fehler auftritt
        """
        logger.debug("username={}", username)

        # https://www.keycloak.org/docs-api/latest/rest-api/#_users:
        # GET /admin/realms/{realm}/users
        user_id: Final = self.keycloak_admin.get_user_id(username)
        logger.debug("user_id={}", user_id)
        exists: Final = user_id is not None
        logger.debug("exists={}", exists)
        return exists

    def email_exists(self, email: str) -> bool:
        """Abfrage, ob eine Email bereits existiert.

        :param email: Die zu überprüfende Email
        :return: True, falls die Email bereits existiert, False sonst
        :rtype: bool
        :raises KeycloakError: Falls mit Keycloak ein Fehler auftritt
        """
        logger.debug("email={}", email)

        # https://www.keycloak.org/docs-api/latest/rest-api/#_users:
        # GET /admin/realms/{realm}/users
        users: Final = self.keycloak_admin.get_users(query={"email": email})
        logger.debug("users={}", users)
        exists: Final = len(users) > 0
        logger.debug("exists={}", exists)
        return exists

    def create_user(self, user: User) -> str:
        """Ein neuer User wird in Keycloak angelegt.

        :param user: Der neue User
        :return: user-id von Keycloak
        :rtype: str
        :raises KeycloakError: Falls mit Keycloak ein Fehler auftritt
        """
        logger.debug("user={}", user)

        # https://www.keycloak.org/docs-api/latest/rest-api/#_users:
        # POST /admin/realms/{realm}/users
        # https://www.keycloak.org/docs-api/latest/rest-api/index.html#UserRepresentation
        user_id: Final = self.keycloak_admin.create_user(
            payload={
                "username": user.username,
                "email": user.email,
                "lastName": user.nachname,
                "firstName": user.vorname,
                "credentials": [{"value": user.password, "type": "password"}],
                "enabled": True,
            },
            exist_ok=False,
        )
        logger.debug("user_id={}", user_id)

        self.keycloak_admin.assign_client_role(
            user_id=user_id, client_id=self.client_uuid, roles=[self.rolle_kunde]
        )
        return user_id

    def remove_all_users(self) -> None:
        """Alle User außer 'admin' aus Keycloak entfernen."""
        # https://www.keycloak.org/docs-api/latest/rest-api/#_users:
        # GET /admin/realms/{realm}/users
        # keycloak_admin.get_users(query={"username": "foo"})
        kc_users: Final = self.keycloak_admin.get_users()
        for kc_user in kc_users:
            if kc_user.get("username") == "admin":
                continue
            # https://www.keycloak.org/docs-api/latest/rest-api/#_users:
            # DELETE /admin/realms/{realm}/users/{user-id}
            self.keycloak_admin.delete_user(kc_user.get("id"))

    def find_user_by_username(self, username: str) -> User | None:
        """Einen User anhand seines Benutzernamens suchen.

        :param username: Benutzername
        :return: Gefundener User mit seinen Rollen oder None
        :rtype: User | None
        :raises KeycloakError: Falls mit Keycloak ein Fehler auftritt
        """
        # https://www.keycloak.org/docs-api/latest/rest-api/#_users:
        # GET /admin/realms/{realm}/users
        kc_users: Final = self.keycloak_admin.get_users({"username": username})
        if not kc_users:
            return None
        kc_user: Final = kc_users[0]
        logger.debug("kc_user={}", kc_user)

        # https://www.keycloak.org/docs-api/latest/rest-api/#_roles
        # GET /admin/realms/{realm}/clients/{client-uuid}/roles/{role-name}/users
        # GET /admin/realms/{realm}/roles/{role-name}/users
        kc_roles: Final[Any] = self.keycloak_admin.get_all_roles_of_user(kc_user["id"])
        kc_client_roles = kc_roles["clientMappings"][keycloak_admin_config.client_id][
            "mappings"
        ]
        logger.debug("kc_client_roles={}", kc_client_roles)

        roles: Final = [Role[role["name"].upper()] for role in kc_client_roles]
        user: Final = User(
            username=kc_user["username"],
            email=kc_user["email"],
            nachname=kc_user["lastName"],
            vorname=kc_user["firstName"],
            roles=roles,
        )
        logger.debug("user={}", user)
        return user
