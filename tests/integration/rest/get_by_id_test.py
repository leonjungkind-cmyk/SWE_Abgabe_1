# ruff: noqa: S101, D103
"""Tests für GET-Requests mit ID als Pfadparameter."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import get
from pytest import mark


# Marker sind in pyproject.toml unter [tool.pytest.ini_options] konfiguriert.
# Mit -m rest bzw. -m get_request lassen sich diese Tests gezielt ausführen.
@mark.rest
@mark.get_request
@mark.parametrize("kunde_id", [30, 1, 20])
def test_get_by_id_admin(kunde_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == kunde_id


@mark.rest
@mark.get_request
@mark.parametrize("kunde_id", [0, 999999])
def test_get_by_id_nicht_gefunden(kunde_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
def test_get_by_id_kunde() -> None:
    # arrange - Kunde 'mueller' darf seinen eigenen Datensatz (ID 1) einsehen
    kunde_id: Final = 1
    token: Final = login(username="mueller")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    kunde_id_response: Final = response_body.get("id")
    assert kunde_id_response is not None
    assert kunde_id_response == kunde_id


@mark.rest
@mark.get_request
@mark.parametrize("kunde_id", [20, 30])
def test_get_by_id_nicht_erlaubt(kunde_id: int) -> None:
    # arrange - Kunde 'mueller' darf fremde Datensätze nicht einsehen
    token: Final = login(username="mueller")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@mark.rest
@mark.get_request
@mark.parametrize("kunde_id", [0, 999999])
def test_get_by_id_nicht_erlaubt_nicht_gefunden(kunde_id: int) -> None:
    # arrange - nicht-existente IDs liefern für Kunden ebenfalls 403 (kein Datenleck)
    token: Final = login(username="mueller")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@mark.rest
@mark.get_request
@mark.parametrize("kunde_id", [30, 1, 20])
def test_get_by_id_ungueltiger_token(kunde_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}XXX"}

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@mark.rest
@mark.get_request
@mark.parametrize("kunde_id", [30, 1, 20])
def test_get_by_id_ohne_token(kunde_id: int) -> None:
    # act
    response: Final = get(f"{rest_url}/{kunde_id}", verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@mark.rest
@mark.get_request
@mark.parametrize("kunde_id,if_none_match", [(20, '"0"'), (30, '"0"')])
def test_get_by_id_etag(kunde_id: int, if_none_match: str) -> None:
    # arrange - gültiger ETag-Wert führt zu 304 Not Modified (keine Datenübertragung)
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_MODIFIED
    assert not response.text


@mark.rest
@mark.get_request
@mark.parametrize("kunde_id,if_none_match", [(30, 'xxx"'), (1, "xxx"), (20, "xxx")])
def test_get_by_id_etag_ungueltig(kunde_id: int, if_none_match: str) -> None:
    # arrange - ungültiger ETag liefert regulären 200-Response mit Körper
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == kunde_id
