# ruff: noqa: S101, D103
"""Tests für Mutations mit GraphQL."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, graphql_url
from httpx import post
from pytest import mark


@mark.graphql
@mark.mutation
def test_create() -> None:
    # arrange
    query: Final = {
        "query": """
            mutation {
                create(
                    kundeInput: {
                        nachname: "Nachnamegraphql"
                        email: "testgraphql@graphql.de"
                        adresse: {
                            strasse: "Graphqlstraße"
                            hausnummer: "1"
                            plz: "99999"
                            ort: "Graphqlort"
                        }
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, verify=ctx)

    # assert
    assert response is not None
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert isinstance(response_body["data"]["create"]["id"], int)
    assert response_body.get("errors") is None


@mark.graphql
@mark.mutation
def test_create_ungueltig() -> None:
    # arrange – ungültige Email und PLZ mit nur 4 Ziffern
    query: Final = {
        "query": """
            mutation {
                create(
                    kundeInput: {
                        nachname: "Nachnamegraphql"
                        email: "falsche_email@"
                        adresse: {
                            strasse: "Graphqlstraße"
                            hausnummer: "1"
                            plz: "1234"
                            ort: "Graphqlort"
                        }
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"] is None
    errors: Final = response_body["errors"]
    assert isinstance(errors, list)
    assert len(errors) == 1
