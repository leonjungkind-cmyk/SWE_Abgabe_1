# ruff: noqa: S101, D103, ARG005
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

"""Unit-Tests für find() von KundeService."""

from datetime import date
from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from kunde.entity import Adresse, Familienstand, Geschlecht, kunde
from kunde.repository import Pageable
from kunde.service import NotFoundError

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
@mark.unit_find
def test_find_by_nachname(kunde_service, session_mock) -> None:
    # Arrange
    nachname = "Mocktest"
    kunde_id = 1
    adresse_mock = Adresse(
        id=1,
        plz="11111",
        ort="Mockort",
        kunde_id=kunde_id,
        kunde=None,
    )
    kunde_mock = kunde(
        id=kunde_id,
        email="mock@email.test",
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
    suchparameter = {"nachname": nachname}
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(kunde)...).all()
    session_mock.scalars.return_value.all.return_value = [kunde_mock]

    # Act
    kundeen_slice = kunde_service.find(
        suchparameter=suchparameter, pageable=pageable
    )

    # Assert
    assert len(kundeen_slice.content) == 1
    assert kundeen_slice.content[0].nachname == nachname


@mark.unit
@mark.unit_find
def test_find_by_nachname_not_found(kunde_service, session_mock) -> None:
    # Arrange
    nachname = "Notfound"
    suchparameter = {"nachname": nachname}
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(kunde)...).all()
    session_mock.scalars.return_value.all.return_value = []

    # Act
    with raises(NotFoundError) as err:
        kunde_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.get("nachname") == nachname  # pyright: ignore[reportOptionalMemberAccess]


@mark.unit
@mark.unit_find
def test_find_by_email(kunde_service, session_mock) -> None:
    # Arrange
    email = "mock@email.test"
    kunde_id = 1
    adresse_mock = Adresse(
        id=1,
        plz="11111",
        ort="Mockort",
        kunde_id=kunde_id,
        kunde=None,
    )
    kunde_mock = kunde(
        id=kunde_id,
        email=email,
        nachname="Mocktest",
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
    suchparameter = {"email": email}
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(kunde)...)
    session_mock.scalar.return_value = kunde_mock

    # Act
    kundeen_slice = kunde_service.find(
        suchparameter=suchparameter, pageable=pageable
    )

    # Assert
    assert len(kundeen_slice.content) == 1
    assert kundeen_slice.content[0].email == email


@mark.unit
@mark.unit_find
def test_find_by_email_not_found(kunde_service, session_mock) -> None:
    # Arrange
    email = "not@found.mock"
    suchparameter = {"email": email}
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(kunde)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(NotFoundError) as err:
        kunde_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.get("email") == email  # pyright: ignore[reportOptionalMemberAccess]
