# ruff: noqa: S101, D103
"""Tests für Authentifizierung und Token-Generierung."""

from http import HTTPStatus
from typing import Final

from common_test import (
    base_url,
    ctx,
    login,
    password_admin,
    timeout,
    token_path,
    username_admin,
)
from httpx import post
from pytest import mark


@mark.login
def test_login_admin() -> None:
    # Vorbereitung & Aktion
    token: Final = login()

    # Überprüfung
    assert isinstance(token, str)
    assert token


@mark.login
def test_login_ungültiges_passwort() -> None:
    # Vorbereitung
    login_data: Final = {"username": username_admin, "password": "UNGÜLTIGES_PASSWORT"}

    # Aktion
    response: Final = post(
        f"{base_url}{token_path}",
        json=login_data,
        verify=ctx,
        timeout=timeout,
    )

    # Überprüfung
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@mark.login
def test_login_ohne_anmeldedaten() -> None:
    # Vorbereitung
    login_data: dict[str, str] = {}

    # Aktion
    response: Final = post(
        f"{base_url}{token_path}",
        json=login_data,
        verify=ctx,
        timeout=timeout,
    )

    # Überprüfung
    assert response.status_code == HTTPStatus.UNAUTHORIZED
