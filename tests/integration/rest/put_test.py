# ruff: noqa: S101, D103
"""Tests für PUT-Requests zum Aktualisieren von Kundendaten."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import put
from pytest import mark

EMAIL_UPDATE: Final = "weber@example.de.put"


@mark.rest
@mark.put_request
def test_put() -> None:
    # arrange
    kunde_id: Final = 40
    if_match: Final = '"0"'
    geaenderter_kunde: Final = {
        "nachname": "Weberput",
        "email": EMAIL_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@mark.rest
@mark.put_request
def test_put_ungueltig() -> None:
    # arrange
    kunde_id: Final = 40
    geaenderter_kunde_ungueltig: Final = {
        "nachname": "Weberput",
        "email": "falsche_email_put@",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "If-Match": '"0"',
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde_ungueltig,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "email" in response.text


@mark.rest
@mark.put_request
def test_put_nicht_vorhanden() -> None:
    # arrange
    kunde_id: Final = 999999
    if_match: Final = '"0"'
    geaenderter_kunde: Final = {
        "nachname": "Weberput",
        "email": EMAIL_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.put_request
def test_put_email_existiert() -> None:
    # arrange - nach test_put hat ID 40 Version 1; Email gehört bereits Kunde 1
    kunde_id: Final = 40
    if_match: Final = '"1"'
    email_vorhanden: Final = "mueller@example.de"
    geaenderter_kunde: Final = {
        "nachname": "Weberput",
        "email": email_vorhanden,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_vorhanden in response.text


@mark.rest
@mark.put_request
def test_put_ohne_versionsnr() -> None:
    # arrange - fehlender If-Match-Header ergibt 428 Precondition Required
    kunde_id: Final = 40
    geaenderter_kunde: Final = {
        "nachname": "Weberput",
        "email": EMAIL_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@mark.rest
@mark.put_request
def test_put_alte_versionsnr() -> None:
    # arrange - veraltete Versionsnummer ergibt 412 Precondition Failed
    kunde_id: Final = 40
    if_match: Final = '"-1"'
    geaenderter_kunde: Final = {
        "nachname": "Weberput",
        "email": EMAIL_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@mark.rest
@mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    # arrange - nicht-numerische Versionsnummer ergibt 412 ohne Antwortinhalt
    kunde_id: Final = 40
    if_match: Final = '"xy"'
    geaenderter_kunde: Final = {
        "nachname": "Weberput",
        "email": EMAIL_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
    assert not response.text


@mark.rest
@mark.put_request
def test_put_versionsnr_ohne_anfuehrungszeichen() -> None:
    # arrange - Versionsnummer ohne umschließende Anführungszeichen ergibt 412
    kunde_id: Final = 40
    if_match: Final = "0"
    geaenderter_kunde: Final = {
        "nachname": "Weberput",
        "email": EMAIL_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kunde_id}",
        json=geaenderter_kunde,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
