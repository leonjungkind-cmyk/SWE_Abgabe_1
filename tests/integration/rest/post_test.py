# ruff: noqa: S101, D103
"""Tests für POST-Requests zum Anlegen neuer Kunden."""

from http import HTTPStatus
from re import search
from typing import Final

from common_test import ctx, login, rest_url
from httpx import post
from pytest import mark


@mark.rest
@mark.post_request
def test_post() -> None:
    # arrange
    neuer_kunde: Final = {
        "nachname": "Neurest",
        "email": "neurest@rest.de",
        "adresse": {
            "strasse": "Teststraße",
            "hausnummer": "1",
            "plz": "99999",
            "ort": "Testort",
        },
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # act
    response: Final = post(
        rest_url,
        json=neuer_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location: Final = response.headers.get("Location")
    assert location is not None
    int_pattern: Final = "[1-9][0-9]*$"
    assert search(int_pattern, location) is not None
    assert not response.text


@mark.rest
@mark.post_request
def test_post_ungueltig() -> None:
    # arrange – ungültige Email und PLZ mit nur 4 Ziffern
    neuer_kunde_ungueltig: Final = {
        "nachname": "Ungueltigrest",
        "email": "falsche_email@",
        "adresse": {
            "strasse": "Teststraße",
            "hausnummer": "1",
            "plz": "1234",
            "ort": "Testort",
        },
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # act
    response: Final = post(
        rest_url,
        json=neuer_kunde_ungueltig,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.text
    assert "email" in body
    assert "plz" in body


@mark.rest
@mark.post_request
def test_post_email_existiert() -> None:
    # arrange – Emailadresse ist bereits einem anderen Kunden zugeordnet
    email_vorhanden: Final = "mueller@example.de"
    neuer_kunde: Final = {
        "nachname": "Neurest",
        "email": email_vorhanden,
        "adresse": {
            "strasse": "Teststraße",
            "hausnummer": "1",
            "plz": "99999",
            "ort": "Testort",
        },
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # act
    response: Final = post(
        rest_url,
        json=neuer_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_vorhanden in response.text


@mark.rest
@mark.post_request
def test_post_ungueltige_json() -> None:
    # arrange – Python-String statt Dictionary führt zu Pydantic-Validierungsfehler
    json_ungueltig: Final = '{"nachname" "Neurest"}'
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # act
    response: Final = post(
        rest_url,
        json=json_ungueltig,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "should be a valid dictionary" in response.text
