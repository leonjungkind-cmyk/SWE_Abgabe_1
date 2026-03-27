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

"""Tests für GET mit Pfadparameter für die ID."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import get
from pytest import mark


# in pyproject.toml bei der Table [tool.pytest.ini_options] gibt es das Array "markers"
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
def test_get_by_id_not_found(kunde_id: int) -> None:
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
    # arrange
    kunde_id: Final = 20
    token: Final = login(username="alice")
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
@mark.parametrize("kunde_id", [1, 30])
def test_get_by_id_not_allowed(kunde_id: int) -> None:
    # arrange
    token: Final = login(username="alice")
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
def test_get_by_id_not_allowed_not_found(kunde_id: int) -> None:
    # arrange
    token: Final = login(username="alice")
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
    # arrange
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
def test_get_by_id_etag_invalid(kunde_id: int, if_none_match: str) -> None:
    # arrange
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
