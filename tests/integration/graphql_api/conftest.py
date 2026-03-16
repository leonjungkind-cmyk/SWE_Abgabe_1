# ruff: noqa: D103
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

"""Fixture für pytest: Neuladen der Datenbank."""

from common_test import check_readiness, db_populate, keycloak_populate
from pytest import fixture

# Erläuterung der Fixtures in tests\test\conftest.py


session_scope = "session"


@fixture(scope=session_scope, autouse=True)
def check_readiness_per_session() -> None:
    check_readiness()
    # Ausgabe in report.html im Wurzelverzeichnis des Projekts
    print("Appserver ist 'ready'")


@fixture(scope=session_scope, autouse=True)
def populate_per_session() -> None:
    """Fixture, um die DB und Keycloak neu zu laden."""
    db_populate()
    print("DB ist neu geladen")
    keycloak_populate()
    print("Keycloak ist neu geladen")
