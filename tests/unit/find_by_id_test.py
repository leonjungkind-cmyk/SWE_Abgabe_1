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

"""Unit-Tests für find_by_id() von PatientService."""

from dataclasses import asdict
from datetime import date
from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from patient.entity import Adresse, Familienstand, Geschlecht, Patient
from patient.security import Role, User
from patient.service import ForbiddenError, NotFoundError, PatientDTO, PatientService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in patient_service.py
    mocker.patch(
        "patient.service.patient_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@mark.unit
@mark.unit_find_by_id
def test_find_by_id(patient_service, session_mock) -> None:
    # Arrange
    patient_id = 1
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
        patient_id=patient_id,
        patient=None,
    )
    patient_mock = Patient(
        id=patient_id,
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
    adresse_mock.patient = patient_mock
    patient_dto_mock = PatientDTO(patient_mock)
    # session.scalar(select(Patient)...)
    session_mock.scalar.return_value = patient_mock

    # Act
    patient_dto = patient_service.find_by_id(patient_id=patient_id, user=user_mock)

    # Assert
    assert asdict(patient_dto) == asdict(patient_dto_mock)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found(patient_service: PatientService, session_mock) -> None:
    # Arrange
    patient_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[Role.ADMIN],
        password="mockpass",
    )
    # session.scalar(select(Patient)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(NotFoundError) as err:
        patient_service.find_by_id(patient_id=patient_id, user=user_mock)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.patient_id == patient_id


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found_not_admin(
    patient_service: PatientService, session_mock
) -> None:
    # Arrange
    patient_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[],
        password="mockpass",
    )
    # session.scalar(select(Patient)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(ForbiddenError) as err:
        patient_service.find_by_id(patient_id=patient_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_admin(patient_service, session_mock) -> None:
    # Arrange
    patient_id = 1
    username = "mocktest"
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.PATIENT],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        patient_id=patient_id,
        patient=None,
    )
    patient_mock = Patient(
        id=patient_id,
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
    adresse_mock.patient = patient_mock
    patient_dto_mock = PatientDTO(patient_mock)
    # session.scalar(select(Patient)...)
    session_mock.scalar.return_value = patient_mock

    # Act
    patient_dto = patient_service.find_by_id(patient_id=patient_id, user=user_mock)

    # Assert
    assert asdict(patient_dto) == asdict(patient_dto_mock)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_other(patient_service, session_mock) -> None:
    # Arrange
    patient_id = 1
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username="other",
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.PATIENT],
        password="mockpass",
    )
    adresse_mock = Adresse(
        id=11,
        plz="11111",
        ort="Mockort",
        patient_id=patient_id,
        patient=None,
    )
    patient_mock = Patient(
        id=patient_id,
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
    adresse_mock.patient = patient_mock
    # session.scalar(select(Patient)...)
    session_mock.scalar.return_value = patient_mock

    # Act
    with raises(ForbiddenError) as err:
        patient_service.find_by_id(patient_id=patient_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError
