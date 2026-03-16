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

"""Tests für POST."""

from http import HTTPStatus
from re import search
from typing import Final

from common_test import ctx, rest_url
from httpx import post
from pytest import mark

token: str | None


@mark.rest
@mark.post_request
def test_post() -> None:
    # arrange
    neuer_patient: Final = {
        "nachname": "Nachnamerest",
        "email": "testrest@rest.de",
        "kategorie": 1,
        "has_newsletter": True,
        "geburtsdatum": "2022-02-01",
        "homepage": "https://rest.de",
        "geschlecht": "W",
        "familienstand": "L",
        "adresse": {"plz": "99999", "ort": "Restort"},
        "rechnungen": [{"betrag": "999.99", "waehrung": "EUR"}],
        "fachaerzte": ["N"],
        "username": "testrest",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_patient,
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
def test_post_invalid() -> None:
    # arrange
    neuer_patient_invalid: Final = {
        "nachname": "falscher_nachname",
        "email": "falsche_email@",
        "kategorie": 11,
        "has_newsletter": True,
        "geburtsdatum": "2022-02-01",
        "homepage": "https://?!",
        "geschlecht": "M",
        "familienstand": "L",
        "adresse": {"plz": "1234", "ort": "Restort"},
        "rechnungen": [{"betrag": "222.2", "waehrung": "EUR"}],
        "fachaerzte": ["N"],
        "username": "testrestinvalid",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_patient_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.text
    assert "nachname" in body
    assert "email" in body
    assert "kategorie" in body
    assert "homepage" in body
    assert "plz" in body


@mark.rest
@mark.post_request
def test_post_email_exists() -> None:
    # arrange
    email_exists: Final = "alice@acme.de"
    neuer_patient: Final = {
        "nachname": "Nachnamerest",
        "email": email_exists,
        "kategorie": 1,
        "has_newsletter": True,
        "geburtsdatum": "2022-02-01",
        "homepage": "https://rest.de",
        "geschlecht": "W",
        "familienstand": "L",
        "adresse": {"plz": "99999", "ort": "Restort"},
        "rechnungen": [{"betrag": "999.99", "waehrung": "EUR"}],
        "fachaerzte": ["N"],
        "username": "emailexists",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_patient,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@mark.rest
@mark.post_request
def test_post_invalid_json() -> None:
    # arrange
    json_invalid: Final = '{"nachname" "Nachname"}'
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=json_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "should be a valid dictionary" in response.text
