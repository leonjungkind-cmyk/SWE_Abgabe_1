# ruff: noqa: S101, D103
"""Tests für DELETE-Requests zum Löschen von Kunden."""

from typing import Final

from common_test import ctx, login, rest_url
from httpx import delete
from pytest import mark


@mark.rest
@mark.delete_request
def test_delete() -> None:
    # arrange
    kunde_id: Final = 60
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = delete(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == 204  # noqa: PLR2004


@mark.rest
@mark.delete_request
def test_delete_nicht_gefunden() -> None:
    # arrange – nicht-existente ID führt ebenfalls zu 204 (idempotentes Löschen)
    kunde_id: Final = 999999
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = delete(
        f"{rest_url}/{kunde_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == 204  # noqa: PLR2004
