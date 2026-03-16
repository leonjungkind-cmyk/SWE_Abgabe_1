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

"""Neuladen von Keycloak im Modus DEV."""

from csv import reader
from pathlib import Path
from typing import Annotated, Final

from fastapi import Depends
from keycloak import KeycloakConnectionError
from loguru import logger

from patient.config import csv_config
from patient.config.dev_modus import dev_keycloak_populate
from patient.security import User, UserService
from patient.security.dependencies import get_user_service
from patient.security.role import Role

__all__ = [
    "KeycloakPopulateService",
    "get_keycloak_populate_service",
    "keycloak_populate",
]


utf8: Final = "utf-8"


class KeycloakPopulateService:
    """Service für das Neuladen von Keycloak im Modus DEV."""

    def __init__(self, user_service: UserService) -> None:
        """Konstruktor mit abhängigem PatientRepository."""
        self.user_service: UserService = user_service

    def populate(self) -> None:
        """User-Daten in Keycloak über die REST-Schnittstelle neu laden."""
        if not dev_keycloak_populate:
            return

        logger.warning(">>> Keycloak wird neu geladen <<<")
        try:
            self._remove_users()
            self._create_users()
            logger.warning(">>> Keycloak wurde neu geladen <<<")
        except KeycloakConnectionError:
            logger.error(">>> Keine Keycloak-Verbindung! Ist Keycloak gestartet? <<<")

    def _remove_users(self) -> None:
        self.user_service.remove_all_users()
        logger.debug("Alle User außer 'admin' geloescht")

    def _create_users(self) -> None:
        logger.debug("Aktuelles Verzeichnis: {}", Path.cwd())
        csv_config_path = Path(csv_config)
        if not csv_config_path.is_file():
            logger.error(f"CSV-Datei {csv_config_path} existiert nicht")
            return
        logger.debug("CSV-Datei: {}", csv_config_path)

        with csv_config_path.open(encoding=utf8) as csv_file:
            csv_reader = reader(csv_file, delimiter=";")
            kopfzeile = True
            for row in csv_reader:
                if kopfzeile:
                    kopfzeile = False
                    continue

                username = row[11]
                if username == "admin":
                    continue

                email = row[3]
                nachname = row[2]
                user = User(
                    username=username,
                    email=email,
                    nachname=nachname,
                    vorname=nachname,
                    roles=[Role.PATIENT],
                    password="p",  # noqa: S106 # NOSONAR
                )
                self.user_service.create_user(user=user)
        logger.debug("Alle User zu 'patient.csv' neu angelegt")


def get_keycloak_populate_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> KeycloakPopulateService:
    """Factory-Funktion für TokenService."""
    return KeycloakPopulateService(user_service)


def keycloak_populate():
    """Keycloak mit Testdaten neu laden, falls im dev-Modus."""
    if dev_keycloak_populate:
        service = get_keycloak_populate_service(get_user_service())
        service.populate()
