# ruff: noqa: S101, D103
"""Tests für Queries mit GraphQL."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, graphql_url, login_graphql
from httpx import post
from pytest import mark


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
                kunde(kundeId: "20") {
                    version
                    nachname
                    email
                    adresse {
                        plz
                        ort
                    }
                    bestellungen {
                        produktname
                        menge
                    }
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
    kunde: Final = data["kunde"]
    assert isinstance(kunde, dict)
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_id_nicht_gefunden() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kunde(kundeId: "999999") {
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
    assert response_body["data"]["kunde"] is None
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
                kunden(suchparameter: {email: "mueller@example.de"}) {
                    id
                    version
                    nachname
                    email
                    adresse {
                        plz
                        ort
                    }
                    bestellungen {
                        produktname
                        menge
                    }
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
    kunden: Final = response_body["data"]["kunden"]
    assert isinstance(kunden, list)
    assert len(kunden) > 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_email_nicht_gefunden() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kunden(suchparameter: {email: "not.found@example.de"}) {
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
    kunden: Final = response_body["data"]["kunden"]
    assert isinstance(kunden, list)
    assert len(kunden) == 0
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
                kunden(suchparameter: {nachname: "Fischer"}) {
                    id
                    version
                    nachname
                    email
                    adresse {
                        plz
                        ort
                    }
                    bestellungen {
                        produktname
                        menge
                    }
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
    kunden: Final = response_body["data"]["kunden"]
    assert isinstance(kunden, list)
    assert len(kunden) > 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_nachname_nicht_gefunden() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kunden(suchparameter: {nachname: "Nichtvorhanden"}) {
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
    kunden: Final = response_body["data"]["kunden"]
    assert isinstance(kunden, list)
    assert len(kunden) == 0
