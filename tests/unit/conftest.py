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

"""Fixture für pytest: Repository, kunde(Write)Service, KeycloakAdmin, UserService."""

from keycloak import KeycloakAdmin
from pytest import fixture
from pytest_mock import MockerFixture

from kunde.repository import KundeRepository
from kunde.security import UserService
from kunde.service import KundeService, KundeWriteService

# "Fixtures" sind Funktionen, die vor den Test-Funktionen ausgefuehrt werden, um z.B.
# wiederholt benoetigte Daten bereitzustellen (URLs, DB-Verbindungen usw.).
# Vgl.: @BeforeEach und @BeforeAll bei JUnit
# Ein Fixture ist eine Funktion, die i.a. in conftest.py implementiert wird und fuer
# alle Test-Funktionen im gleichen Verzeichnis verwendet werden kann.
# Eine Fixture-Funktion wir dann als erstes Argument an die Test-Funktion übergeben
# oder hat das Argument autouse=True fuer die implizite Uebergabe.
# Jedes Fixture hat einen Scope: function (= default), class, module, package, session.
# Die Reihenfolge ist: session > package > module > class > function (~ BeforeEach).
# module: 1x die Fixture-Funktionen pro Datei mit Test-Funktionen aufrufen
# session: 1x die Fixture-Funktionen in diesem Verzeichnis aufrufen
# session verwendet man fuer aufwaendige Operationen, z.B. Test-DB laden.

# https://docs.pytest.org/en/stable/explanation/fixtures.html
# https://docs.pytest.org/en/stable/how-to/fixtures.html
# Anzeige aller fixtures ausgehend vom Wurzelverzeichnis:   uv run pytest --fixtures


@fixture()
def kunde_repository() -> KundeRepository:
    """Fixture für KundeRepository."""
    return KundeRepository()


@fixture
def kunde_service(kunde_repository: KundeRepository) -> KundeService:
    """Fixture für KundeService."""
    return KundeService(kunde_repository)


@fixture
def keycloak_admin_mock(mocker: MockerFixture) -> KeycloakAdmin:
    """Patching von KeycloakAdmin() innerhalb von UserService."""
    keycloak_admin_cls_mock = mocker.patch(
        "kunde.security.user_service.KeycloakAdmin"
    )
    return keycloak_admin_cls_mock.return_value


@fixture
def user_service(keycloak_admin_mock) -> UserService:
    """Patching von KeycloakAdmin.get_client_id() fuer UserService."""
    uuid_mock = "12345678-1234-1234-1234-123456789012"
    keycloak_admin_mock.get_client_id.return_value = uuid_mock
    # Patching von keycloak_admin.get_client_roles()
    kunde_rolle_mock = {
        "id": uuid_mock,
        "name": "kunde",
        "description": "",
        "composite": False,
        "clientRole": True,
        "containerId": uuid_mock,
    }
    keycloak_admin_mock.get_client_roles.return_value = [kunde_rolle_mock]
    return UserService()


@fixture
def kunde_write_service(
    kunde_repository: KundeRepository, user_service: UserService
) -> KundeWriteService:
    """Fixture für KundeWriteService."""
    return KundeWriteService(kunde_repository, user_service)
