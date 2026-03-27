# ruff: noqa: S101, S106, D103, ARG005
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

"""Unit-Tests für find_by_id() von KundeService."""

from dataclasses import asdict
from datetime import date
from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from kunde.entity import Adresse, Familienstand, Geschlecht, kunde
from kunde.security import Role, User
from kunde.service import ForbiddenError, NotFoundError, KundeDTO, KundeService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in kunde_service.py
    mocker.patch(
        "kunde.service.kunde_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@mark.unit
@mark.unit_find_by_id
def test_find_by_id(kunde_service, session_mock) -> None:
    # Arrange
    kunde_id = 1
    username = "mocktest"
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.ADMIN],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        kunde_id=kunde_id,
        kunde=None,
    )
    kunde_mock = kunde(
        id=kunde_id,
        email=email,
        nachname=nachname,
        kategorie=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        geschlecht=Geschlecht.MAENNLICH,
        familienstand=Familienstand.LEDIG,
        homepage="https://www.test.de",
        username=username,
        adresse=adresse_mock,
        fachaerzte=[],
        rechnungen=[],
    )
    adresse_mock.kunde = kunde_mock
    kunde_dto_mock = KundeDTO(kunde_mock)
    # session.scalar(select(kunde)...)
    session_mock.scalar.return_value = kunde_mock

    # Act
    kunde_dto = kunde_service.find_by_id(kunde_id=kunde_id, user=user_mock)

    # Assert
    assert asdict(kunde_dto) == asdict(kunde_dto_mock)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found(kunde_service: KundeService, session_mock) -> None:
    # Arrange
    kunde_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[Role.ADMIN],
        password="mockpass",
    )
    # session.scalar(select(kunde)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(NotFoundError) as err:
        kunde_service.find_by_id(kunde_id=kunde_id, user=user_mock)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.kunde_id == kunde_id


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found_not_admin(
    kunde_service: KundeService, session_mock
) -> None:
    # Arrange
    kunde_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[],
        password="mockpass",
    )
    # session.scalar(select(kunde)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(ForbiddenError) as err:
        kunde_service.find_by_id(kunde_id=kunde_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_admin(kunde_service, session_mock) -> None:
    # Arrange
    kunde_id = 1
    username = "mocktest"
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.kunde],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        kunde_id=kunde_id,
        kunde=None,
    )
    kunde_mock = kunde(
        id=kunde_id,
        email=email,
        nachname=nachname,
        kategorie=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        geschlecht=Geschlecht.MAENNLICH,
        familienstand=Familienstand.LEDIG,
        homepage="https://www.test.de",
        username=username,
        adresse=adresse_mock,
        fachaerzte=[],
        rechnungen=[],
    )
    adresse_mock.kunde = kunde_mock
    kunde_dto_mock = KundeDTO(kunde_mock)
    # session.scalar(select(kunde)...)
    session_mock.scalar.return_value = kunde_mock

    # Act
    kunde_dto = kunde_service.find_by_id(kunde_id=kunde_id, user=user_mock)

    # Assert
    assert asdict(kunde_dto) == asdict(kunde_dto_mock)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_other(kunde_service, session_mock) -> None:
    # Arrange
    kunde_id = 1
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username="other",
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.kunde],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        kunde_id=kunde_id,
        kunde=None,
    )
    kunde_mock = kunde(
        id=kunde_id,
        email=email,
        nachname=nachname,
        kategorie=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        geschlecht=Geschlecht.MAENNLICH,
        familienstand=Familienstand.LEDIG,
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse_mock,
        fachaerzte=[],
        rechnungen=[],
    )
    adresse_mock.kunde = kunde_mock
    # session.scalar(select(kunde)...)
    session_mock.scalar.return_value = kunde_mock

    # Act
    with raises(ForbiddenError) as err:
        kunde_service.find_by_id(kunde_id=kunde_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError
