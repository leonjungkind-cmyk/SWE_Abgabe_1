# ruff: noqa: S101, D103
"""Tests für GET-Requests mit Query-Parametern."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import get
from pytest import mark


@mark.rest
@mark.get_request
@mark.parametrize("email", ["mueller@example.de", "schmidt@example.de"])
def test_get_by_email(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    kunde = content[0]
    assert kunde is not None
    assert kunde.get("email") == email
    assert kunde.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("email", ["nicht@vorhanden.com", "foo.bar@example.de"])
def test_get_by_email_nicht_gefunden(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("teil", ["Fischer", "er"])
def test_get_by_nachname(teil: str) -> None:
    # arrange
    params = {"nachname": teil}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    content: Final = response_body["content"]
    for k in content:
        nachname = k.get("nachname")
        assert nachname is not None and isinstance(nachname, str)
        assert teil.lower() in nachname.lower()
        assert k.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("nachname", ["Notfound", "Xyz-Bar"])
def test_get_by_nachname_nicht_gefunden(nachname: str) -> None:
    # arrange
    params = {"nachname": nachname}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("teil", ["er", "mann"])
def test_get_nachnamen(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/nachnamen/{teil}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    nachnamen: Final = response.json()
    assert isinstance(nachnamen, list)
    assert len(nachnamen) > 0
    for nachname in nachnamen:
        assert teil.lower() in nachname.lower()


@mark.rest
@mark.get_request
@mark.parametrize("teil", ["xxx", "zzz"])
def test_get_nachnamen_nicht_gefunden(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/nachnamen/{teil}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND
