"""Neuladen von Keycloak im Modus DEV."""

from csv import DictReader
from pathlib import Path
from typing import Annotated, Final

from fastapi import Depends
from keycloak import KeycloakConnectionError
from loguru import logger

from kunde.config import csv_config
from kunde.config.dev_modus import dev_keycloak_populate
from kunde.security import User, UserService
from kunde.security.dependencies import get_user_service
from kunde.security.role import Role

__all__ = [
    "KeycloakPopulateService",
    "get_keycloak_populate_service",
    "keycloak_populate",
]


utf8: Final = "utf-8"


class KeycloakPopulateService:
    """Service für das Neuladen von Keycloak im Modus DEV."""

    def __init__(self, user_service: UserService) -> None:
        """Konstruktor mit abhängigem UserService."""
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
            logger.error("CSV-Datei {} existiert nicht", csv_config_path)
            return

        logger.debug("CSV-Datei: {}", csv_config_path)

        with csv_config_path.open(encoding=utf8, newline="") as csv_file:
            csv_reader = DictReader(csv_file, delimiter=",")

            for row in csv_reader:
                email = (row.get("email") or "").strip()
                nachname = (row.get("nachname") or "").strip()
                username = (row.get("username") or "").strip()

                if not username:
                    if email:
                        username = email.split("@")[0]
                    else:
                        logger.warning(
                            "Zeile ohne username und ohne email übersprungen: {}",
                            row,
                        )
                        continue

                if username == "admin":
                    continue

                if not email:
                    logger.warning(
                        "Zeile ohne email übersprungen: {}",
                        row,
                    )
                    continue

                if not nachname:
                    nachname = username

                user = User(
                    username=username,
                    email=email,
                    nachname=nachname,
                    vorname=nachname,
                    roles=[Role.kunde],
                    password="p",  # noqa: S106 # NOSONAR
                )
                self.user_service.create_user(user=user)

        logger.debug("Alle User zu 'kunde.csv' neu angelegt")


def get_keycloak_populate_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> KeycloakPopulateService:
    """Factory-Funktion für KeycloakPopulateService."""
    return KeycloakPopulateService(user_service)


def keycloak_populate() -> None:
    """Keycloak mit Testdaten neu laden, falls im dev-Modus."""
    if dev_keycloak_populate:
        service = get_keycloak_populate_service(get_user_service())
        service.populate()
