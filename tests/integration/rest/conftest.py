# ruff: noqa: D103
"""Fixtures für REST-Integrationstests: DB und Keycloak einmalig pro Session laden."""

from common_test import check_readiness, db_populate, keycloak_populate
from pytest import fixture

# Jedes Fixture hat einen Scope: function (default), class, module, package, session.
# session: Fixture-Funktionen werden einmalig für die gesamte Test-Session aufgerufen.
# Damit werden aufwändige Operationen (DB/Keycloak neu laden) nur einmal ausgeführt.
# https://docs.pytest.org/en/stable/explanation/fixtures.html

session_scope = "session"


@fixture(scope=session_scope, autouse=True)
def check_readiness_per_session() -> None:
    check_readiness()
    print("Appserver ist bereit")


@fixture(scope=session_scope, autouse=True)
def populate_per_session() -> None:
    """DB und Keycloak einmalig zu Beginn der Test-Session neu laden."""
    db_populate()
    print("DB wurde neu geladen")
    keycloak_populate()
    print("Keycloak wurde neu geladen")
