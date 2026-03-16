# ruff: noqa: S101, D103
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

"""Tests für Queries mit GraphQL."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, graphql_url, login_graphql
from httpx import post
from pytest import mark

GRAPHQL_PATH: Final = "/graphql"


@mark.graphql
@mark.query
def test_query_id() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                patient(patientId: "20") {
                    version
                    nachname
                    email
                    kategorie
                    hasNewsletter
                    geburtsdatum
                    homepage
                    geschlecht
                    familienstand
                    adresse {
                        plz
                        ort
                    }
                    fachaerzte
                    username
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    data: Final = response_body["data"]
    assert data is not None
    patient: Final = data["patient"]
    assert isinstance(patient, dict)
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_id_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                patient(patientId: "999999") {
                    nachname
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"]["patient"] is None
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_email() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                patienten(suchparameter: {email: "admin@acme.com"}) {
                    id
                    version
                    nachname
                    email
                    kategorie
                    hasNewsletter
                    geburtsdatum
                    homepage
                    geschlecht
                    familienstand
                    adresse {
                        plz
                        ort
                    }
                    fachaerzte
                    username
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    patienten: Final = response_body["data"]["patienten"]
    assert isinstance(patienten, list)
    assert len(patienten) > 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_email_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                patienten(suchparameter: {email: "not.found@acme.com"}) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    patienten: Final = response_body["data"]["patienten"]
    assert isinstance(patienten, list)
    assert len(patienten) == 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_nachname() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                patienten(suchparameter: {nachname: "Alice"}) {
                    id
                    version
                    nachname
                    email
                    kategorie
                    hasNewsletter
                    geburtsdatum
                    homepage
                    geschlecht
                    familienstand
                    adresse {
                        plz
                        ort
                    }
                    fachaerzte
                    username
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    patienten: Final = response_body["data"]["patienten"]
    assert isinstance(patienten, list)
    assert len(patienten) > 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_nachname_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                patienten(suchparameter: {nachname: "Nichtvorhanden"}) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    patienten: Final = response_body["data"]["patienten"]
    assert isinstance(patienten, list)
    assert len(patienten) == 0
